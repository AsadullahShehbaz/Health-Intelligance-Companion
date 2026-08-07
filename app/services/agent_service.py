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


def _build_initial_state(req: AgentRequest) -> dict:
    return {
        "patient_id": req.patient_id,
        "raw_input": req.query,
        "has_image": req.image_base64 is not None,
        "image_base64": req.image_base64,
        "detected_lang": "",
        "english_query": "",
        "rewritten_query": "",
        "needs_rag": False,
        "save_memory": False,
        "retrieved_docs": [],
        "retrieval_decision": "",
        "recent_memory": [],
        "patient_facts": [],
        "answer": "",
        "final_response": "",
    }


# Neon autosuspends an idle compute and kills its connections. The pool
# reconnects on checkout, but the *first* query on a fresh connection can
# still abort while the compute is waking (the pool's ping races the wake).
# Retrying a transient OperationalError absorbs that — the failure in the
# traceback is the checkpointer's very first read, before any node runs, so
# a retry is a clean restart (LangGraph resumes from the checkpoint).
_MAX_DB_RETRIES = 2
_RETRY_DELAY_SECONDS = 0.5


async def run_agent(req: AgentRequest) -> AgentResponse:
    initial_state = _build_initial_state(req)
    config = {"configurable": {"thread_id": req.patient_id}}

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
        needs_rag=result["needs_rag"],
        retrieval_decision=result.get("retrieval_decision") or None,
        sources=[d["source"] for d in result.get("retrieved_docs", [])[:3]],
        save_memory=result["save_memory"],
    )