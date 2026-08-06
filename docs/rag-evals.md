Good instinct — a hallucination/accuracy comparison is exactly the kind of result that makes "Corrective RAG" a real contribution rather than just an added feature. Here's a step-by-step evaluation plan that plugs into what you've already built.

## Evaluation Day 1 — Build a held-out test set

Don't reuse training data. Pull a small, fixed set of questions you did *not* train on, ideally with known-correct reference answers so you can score against something.

```python
# eval/test_set.py
TEST_CASES = [
    {
        "query": "What are the symptoms of vitamin D deficiency?",
        "reference": "Fatigue, bone pain, muscle weakness, and mood changes...",
        "category": "in_distribution",   # covered well by your knowledge base
    },
    {
        "query": "What is the recommended dosage of metformin for a newly diagnosed type 2 diabetic?",
        "reference": "...",
        "category": "in_distribution",
    },
    {
        "query": "What's the latest WHO guidance on mpox vaccination published this year?",
        "reference": None,   # unknown/recent — tests whether RAG's web fallback helps
        "category": "out_of_distribution",
    },
    # aim for 30-50 cases total, mixed:
    # - in_distribution (covered by disease_db/MedQA/PubMed/ChatDoctor)
    # - out_of_distribution (should trigger the "incorrect" correction path)
    # - ambiguous/tricky phrasing (tests the "ambiguous" middle path)
]
```

A good split: ~60% in-distribution, ~25% out-of-distribution, ~15% deliberately ambiguous phrasing. This directly stresses all three branches of your `evaluate_relevance()` logic — which is the thing you actually want to demonstrate works.

## Evaluation Day 2 — Run both pipelines, capture everything

```python
# eval/run_eval.py
import json, time
from app.core.llm import llm
from app.core.rag.corrective_rag import corrective_retrieve
from eval.test_set import TEST_CASES


def run_finetuned_only(query: str) -> dict:
    start = time.time()
    response = llm.create_chat_completion(
        messages=[{"role": "user", "content": query}],
        temperature=0.7,
        max_tokens=300,
    )
    return {
        "answer": response["choices"][0]["message"]["content"],
        "latency": time.time() - start,
    }


def run_rag(query: str) -> dict:
    start = time.time()
    result = corrective_retrieve(query)
    context = "\n\n".join(d["text"][:300] for d in result["docs"][:3])
    prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"

    response = llm.create_chat_completion(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=300,
    )
    return {
        "answer": response["choices"][0]["message"]["content"],
        "latency": time.time() - start,
        "retrieval_decision": result["decision"],
        "avg_score": result["avg_score"],
        "sources": [d["source"] for d in result["docs"][:3]],
    }


results = []
for case in TEST_CASES:
    print(f"Running: {case['query'][:60]}...")
    results.append({
        "query": case["query"],
        "category": case["category"],
        "reference": case["reference"],
        "finetuned_only": run_finetuned_only(case["query"]),
        "rag": run_rag(case["query"]),
    })

json.dump(results, open("eval/results_raw.json", "w"), indent=2)
print(f"Done: {len(results)} cases")
```

Run this once, save the raw JSON — you don't want to re-hit the LLM every time you tweak scoring.

Good — that's a cleaner target than what I gave you. Let's align the RAG evaluation to these exact same 5 metrics so your comparison table is apples-to-apples in the FYP report. Only Evaluation Day 3 needs to change.

## Updated Evaluation Day 3 — Score with your 5 metrics

Perplexity works a bit differently here — it needs token-level logprobs from `llama-cpp-python`, not just the generated text, so it has to be computed at generation time, not after.

```python
# eval/score.py
import json
import math
import statistics
from rouge_score import rouge_scorer
from bert_score import score as bert_score

results = json.load(open("eval/results_raw.json"))
scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)

# ── ROUGE-1 / ROUGE-2 / ROUGE-L ──────────────────────
scored = []
for r in results:
    if not r["reference"]:
        continue  # OOD cases scored separately (Day 4)

    ft = scorer.score(r["reference"], r["finetuned_only"]["answer"])
    rag = scorer.score(r["reference"], r["rag"]["answer"])

    scored.append({
        "query": r["query"],
        "category": r["category"],
        "ft_rouge1": ft["rouge1"].fmeasure,
        "ft_rouge2": ft["rouge2"].fmeasure,
        "ft_rougeL": ft["rougeL"].fmeasure,
        "rag_rouge1": rag["rouge1"].fmeasure,
        "rag_rouge2": rag["rouge2"].fmeasure,
        "rag_rougeL": rag["rougeL"].fmeasure,
    })

# ── BERTScore F1 (batched) ───────────────────────────
refs        = [r["reference"] for r in results if r["reference"]]
ft_answers  = [r["finetuned_only"]["answer"] for r in results if r["reference"]]
rag_answers = [r["rag"]["answer"] for r in results if r["reference"]]

_, _, ft_f1  = bert_score(ft_answers, refs, lang="en")
_, _, rag_f1 = bert_score(rag_answers, refs, lang="en")

for i, s in enumerate(scored):
    s["ft_bertscore"]  = ft_f1[i].item()
    s["rag_bertscore"] = rag_f1[i].item()

json.dump(scored, open("eval/scored.json", "w"), indent=2)

def avg(key):
    return statistics.mean(s[key] for s in scored)

print("=" * 55)
print("  RAG vs Fine-Tuned-Only — Comparison")
print("=" * 55)
print(f"  ROUGE-1      : FT {avg('ft_rouge1'):.4f}  |  RAG {avg('rag_rouge1'):.4f}")
print(f"  ROUGE-2      : FT {avg('ft_rouge2'):.4f}  |  RAG {avg('rag_rouge2'):.4f}")
print(f"  ROUGE-L      : FT {avg('ft_rougeL'):.4f}  |  RAG {avg('rag_rougeL'):.4f}")
print(f"  BERTScore F1 : FT {avg('ft_bertscore'):.4f}  |  RAG {avg('rag_bertscore'):.4f}")
print("=" * 55)
```

## Perplexity — needs a separate pass with logprobs

`llama-cpp-python` gives you per-token logprobs if you pass `logprobs=True`. Perplexity is computed from the model's confidence on generating the *reference* answer given the prompt (not on its own generated answer — that's the standard definition, and it's what makes it comparable to your fine-tuning report).

```python
# eval/perplexity.py
import math
from app.core.llm import llm


def compute_perplexity(prompt: str, reference: str) -> float:
    """
    Perplexity of the reference answer conditioned on the prompt.
    Lower = model assigns higher probability to the correct answer.
    """
    full_text = f"{prompt}\n{reference}"

    output = llm(
        full_text,
        max_tokens=0,      # don't generate — just score existing tokens
        logprobs=True,
        echo=True,
    )

    token_logprobs = output["choices"][0]["logprobs"]["token_logprobs"]
    # drop None entries (first token has no logprob)
    logprobs = [lp for lp in token_logprobs if lp is not None]

    avg_neg_logprob = -sum(logprobs) / len(logprobs)
    return math.exp(avg_neg_logprob)
```

```python
# eval/run_perplexity.py
import json
import statistics
from eval.perplexity import compute_perplexity
from eval.test_set import TEST_CASES
from app.core.rag.corrective_rag import corrective_retrieve

ft_ppls, rag_ppls = [], []

for case in TEST_CASES:
    if not case["reference"]:
        continue

    query, reference = case["query"], case["reference"]

    # fine-tuned-only prompt (bare query)
    ft_ppl = compute_perplexity(query, reference)
    ft_ppls.append(ft_ppl)

    # RAG prompt (query + retrieved context)
    result = corrective_retrieve(query)
    context = "\n\n".join(d["text"][:300] for d in result["docs"][:3])
    rag_prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
    rag_ppl = compute_perplexity(rag_prompt, reference)
    rag_ppls.append(rag_ppl)

    print(f"{query[:50]:50s}  FT={ft_ppl:.2f}  RAG={rag_ppl:.2f}")

print(f"\nAvg Perplexity — Fine-tuned only : {statistics.mean(ft_ppls):.2f}")
print(f"Avg Perplexity — RAG (with context): {statistics.mean(rag_ppls):.2f}")
```

Note the direction you'd expect: if retrieval is genuinely relevant, RAG perplexity on the *correct* reference answer should drop below fine-tuned-only, since the context makes the right answer more predictable. If it doesn't drop — or gets worse — that's a real, reportable finding (could mean your context window is too small at 2048, or retrieved chunks are noisy), not a bug to hide.

## Final report table

```
=============================================
  RAG vs Fine-Tuned-Only — FINAL EVALUATION
  BioMistral-7B (fine-tuned) | Corrective RAG
=============================================
                    Fine-tuned only    RAG
  Perplexity        X.XX               X.XX      (lower better)
  ROUGE-1           0.XXXX             0.XXXX
  ROUGE-2           0.XXXX             0.XXXX
  ROUGE-L           0.XXXX             0.XXXX
  BERTScore F1      0.XXXX             0.XXXX
=============================================
```

One practical note before you run this: `n_ctx=2048` in your `core/llm.py` is going to be tight once you add ~900 chars of retrieved context on top of the query — check that `_build_prompt`'s context + question + `max_tokens` doesn't get silently truncated by llama-cpp, or your perplexity/ROUGE numbers for RAG will be measuring a cut-off prompt rather than the real one. Worth a quick token-count sanity check on your longest test case before the full run.


## Evaluation Day 4 — Hallucination check for out-of-distribution cases

This is the metric that actually justifies "Corrective" RAG, since ROUGE/BERTScore need a reference and your OOD cases don't have one. Score these differently: manual or LLM-judged factual grounding.

A simple, defensible approach for an FYP — a small rubric you (or a second LLM call) score 0–2:

```python
# eval/hallucination_check.py
GROUNDING_PROMPT = """
Question: {query}
Retrieved sources used: {sources}
Model answer: {answer}

Rate the answer on this scale:
0 = answer contains claims not supported by the sources and not general medical knowledge
1 = answer is mostly grounded, with minor unsupported claims
2 = answer is fully grounded in the sources or safe, general medical knowledge

Respond with only the number.
"""
```

Run this rubric prompt through your fine-tuned model itself (or manually score 30 cases by hand — for an FYP evaluation section, manual scoring of a modest N is completely standard and often *more* credible than a self-judged LLM score). Tabulate:

| Category | Fine-tuned only | RAG |
|---|---|---|
| In-distribution (avg ROUGE-L) | ... | ... |
| In-distribution (avg BERTScore) | ... | ... |
| Out-of-distribution grounding score (0–2) | ... | ... |
| Avg latency (s) | ... | ... |

## Evaluation Day 5 — Write it up

For `docs/rag-evaluation.md`, structure it the same way your existing `training-report.md` reads:
- Test set composition (N cases, split by category)
- Metrics used and why (ROUGE-L / BERTScore for grounded answers, manual grounding score for OOD)
- Results table above
- 2–3 concrete qualitative examples: one where RAG's correction step clearly fixed a hallucination, one where retrieval was "correct" and RAG matched fine-tuned quality, one failure case (RAG doesn't always win — showing this is more credible for an FYP than only positive results)
- Latency tradeoff — RAG will be slower (embedding + Qdrant search added), so report that honestly

One thing worth flagging: your `avg_score` field from `corrective_retrieve()` is itself useful evidence — plotting retrieval decision (`correct`/`ambiguous`/`incorrect`) against whether RAG's answer beat the fine-tuned one is a nice extra chart that directly validates your relevance-threshold design, not just the final output quality.