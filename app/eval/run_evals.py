# eval/run_eval.py
import json, os, time
from pathlib import Path
from app.core.llm import llm
from app.core.rag.corrective_rag import corrective_retrieve
from app.eval.test_set import TEST_CASES


def response_mentions_known_patient_profile(response: str, patient_profile: dict) -> bool:
    """Cheap adherence guard: the model should mention at least one known
    patient fact when a patient profile was provided in context."""
    if not patient_profile:
        return True

    text = (response or "").lower()
    for key, value in patient_profile.items():
        if value and value.lower() in text:
            return True
        if key.lower() in text and value and any(part.lower() in text for part in str(value).split()[:3]):
            return True
    return False


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

out_path = Path(__file__).resolve().parent / "results_raw.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)
print(f"Done: {len(results)} cases -> {out_path}")