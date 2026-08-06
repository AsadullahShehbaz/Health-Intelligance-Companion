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