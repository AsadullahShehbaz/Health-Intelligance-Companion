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