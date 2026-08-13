# app/services/agent_service.py
import asyncio

import psycopg
from starlette.concurrency import run_in_threadpool

from app.agent.graph import build_health_agent
from app.schemas.agent import AgentRequest, AgentResponse
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

# Compiled once at import time — reused across requests, same pattern
# as loading `llm` once in core/llm.py
agent = build_health_agent()


def _build_initial_state(req: AgentRequest, ocr_text: str = "") -> dict:
    return {
        "patient_id": req.patient_id,
        "raw_input": req.query,
        "ocr_context": ocr_text,
        "final_response": "",
        "detected_lang": "",
        "needs_rag": False,
        "retrieval_decision": "",
        "retrieved_docs": [],
        "messages": [],
        "tool_call_count": 0,
    }


# Neon autosuspends an idle compute and kills its connections. The pool
# reconnects on checkout, but the *first* query on a fresh connection can
# still abort while the compute is waking (the pool's ping races the wake).
# Retrying a transient OperationalError absorbs that — the failure in the
# traceback is the checkpointer's very first read, before any node runs, so
# a retry is a clean restart (LangGraph resumes from the checkpoint).
_MAX_DB_RETRIES = 2
_RETRY_DELAY_SECONDS = 0.5


async def run_agent(req: AgentRequest, ocr_text: str = "") -> AgentResponse:
    initial_state = _build_initial_state(req, ocr_text)
    # One thread per conversation. Defaults to patient_id so older clients
    # (and pre-sidebar data) keep resuming the single per-patient thread.
    thread_id = req.thread_id or req.patient_id
    # recursion_limit is LangGraph's own graph-level safety net, on top of
    # MAX_TOOL_CALLS inside the agent node — belt and suspenders against a
    # tool loop that never calls final_answer.
    config = {"configurable": {"thread_id": thread_id}, "recursion_limit": 15}

    for attempt in range(_MAX_DB_RETRIES + 1):
        try:
            result = await run_in_threadpool(agent.invoke, initial_state, config)
            break
        except psycopg.OperationalError as e:
            if attempt >= _MAX_DB_RETRIES:
                logger.exception("Agent graph execution failed after %d retries", attempt + 1)
                raise
            logger.warning(
                "Transient DB error during agent invoke (attempt %d/%d), retrying: %s",
                attempt + 1,
                _MAX_DB_RETRIES,
                e,
            )
            await asyncio.sleep(_RETRY_DELAY_SECONDS)
        except Exception:
            logger.exception("Agent graph execution failed")
            raise

    return AgentResponse(
        answer=result["final_response"],
        detected_lang=result["detected_lang"],
        needs_rag=result.get("needs_rag", False),
        retrieval_decision=result.get("retrieval_decision") or None,
        sources=[d.get("source") for d in result.get("retrieved_docs", [])[:3] if d.get("source")],
        save_memory=result.get("saved_memory", False),
    )