"""
test_week6_agent.py — run the tool-binding agent loop against a live backend.

Direct-run script (not pytest), same convention as the other app/tests scripts.
All four cases run on ONE patient_id so you can confirm the fever from case 2
is actually recalled in case 3 via fetch_patient_facts — the real proof the
fact-memory redesign works, and that the loop terminates (no hang) for both
the happy path and the tool-calling path.

    conda activate ft-project
    python app/tests/test_week6_agent.py [max_cases]

Passing an optional max_cases (1-4) limits how many turns run — handy for a
quick smoke test before the full ~30-minute live run.
"""
import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo root, so `import app` works

import psycopg

from app.db.lifespan import checkpointer, store
from app.services.agent_service import run_agent
from app.schemas.agent import AgentRequest

# Neon autosuspends an idle compute; waking it can kill the first connection
# mid-setup (AdminShutdown is an OperationalError subclass) or stall it long
# enough to hit the pool's checkout timeout. Same retry pattern as
# agent_service.run_agent, but with more patience for the slow wake.
_MAX_DB_RETRIES = 5
_RETRY_DELAY_SECONDS = 5.0


def _setup_backends():
    # The checkpointer/store backends are set up by the FastAPI lifespan;
    # running run_agent directly (no server) needs those tables to exist.
    for attempt in range(_MAX_DB_RETRIES + 1):
        try:
            checkpointer.setup()
            store.setup()
            return
        except psycopg.OperationalError as e:
            if attempt >= _MAX_DB_RETRIES:
                raise
            print(
                f"setup failed (attempt {attempt + 1}/{_MAX_DB_RETRIES + 1}), "
                f"retrying: {e}"
            )
            time.sleep(_RETRY_DELAY_SECONDS)


async def main():
    _setup_backends()

    cases = [
        "hello, how are you",
        "I have had a fever and body pain for three days",
        "is this the same fever from before",       # tests fetch_patient_facts
        "I'm really scared about this",              # tests save_emotional_state
    ]
    if len(sys.argv) > 1:
        cases = cases[: int(sys.argv[1])]
    for q in cases:
        r = await run_agent(AgentRequest(patient_id="test_patient_01", query=q))
        print(f"\nQ: {q}\nRAG: {r.needs_rag} | Saved: {r.save_memory}\nA: {r.answer[:200]}")


if __name__ == "__main__":
    asyncio.run(main())