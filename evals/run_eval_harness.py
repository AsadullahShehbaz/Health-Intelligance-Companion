# evals/run_eval_harness.py
import asyncio, json, os, sys, time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.agent_service import run_agent
from app.schemas.agent import AgentRequest
from evals.golden_dataset import GOLDEN

OUT = "evals/eval_results.json"

async def run_one(case, patient_id="eval_patient_001", thread_id=None):
    """Run one query through the agent and capture everything."""
    t0 = time.monotonic()
    req = AgentRequest(
        patient_id=patient_id,
        query=case["question"],
        thread_id=thread_id or f"eval_{case['id']}"
    )
    try:
        resp = await run_agent(req)
        elapsed = time.monotonic() - t0
        return {
            **case,
            "actual_answer": resp.answer,
            "needs_rag_predicted": resp.needs_rag,
            "retrieval_decision": resp.retrieval_decision,
            "sources": resp.sources,
            "save_memory": resp.save_memory,
            "latency_sec": round(elapsed, 2),
            "error": None
        }
    except Exception as e:
        return {**case, "actual_answer": "", "error": str(e),
                "latency_sec": round(time.monotonic()-t0, 2)}

async def main():
    # IMPORTANT: use a FRESH thread per case so memory doesn't bleed across
    results = []
    for case in GOLDEN:
        print(f"[{case['id']}] {case['question'][:50]}...")
        # New thread per case = isolated state
        r = await run_one(case, thread_id=f"eval_iso_{case['id']}")
        results.append(r)
        print(f"    → RAG={r.get('needs_rag_predicted')} | lat={r['latency_sec']}s")

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Saved {len(results)} traces to {OUT}")

if __name__ == "__main__":
    asyncio.run(main())
