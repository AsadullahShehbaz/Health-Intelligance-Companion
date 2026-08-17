# app/services/agent_service.py
import asyncio
import time

import psycopg
from starlette.concurrency import run_in_threadpool

from app.agent.graph import build_health_agent
from app.db.pool import run_with_retry
from app.schemas.agent import AgentRequest, AgentResponse
from app.services.title_service import generate_thread_title
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

# Compiled once at import time — reused across requests, same pattern
# as loading `llm` once in core/llm.py
agent = build_health_agent()
# File: app/services/agent_service.py

from psycopg import OperationalError, DatabaseError

logger = get_logger(__name__)

async def execute_graph_with_retry(graph, inputs, config, retries=3, delay=1.5):
    for attempt in range(1, retries + 1):
        try:
            return await graph.ainvoke(inputs, config=config)
        except (OperationalError, DatabaseError) as db_err:
            logger.warning(f"⚠️ DB Connection error during graph execution (Attempt {attempt}/{retries}): {db_err}")
            if attempt == retries:
                raise db_err
            await asyncio.sleep(delay * attempt)
        except Exception as e:
            raise e

def _build_initial_state(req: AgentRequest, ocr_text: str = "") -> dict:
    return {
        "patient_id": req.patient_id,
        "raw_input": req.query,
        "ocr_context": ocr_text,
        "answer": "",
        "final_response": "",
        "detected_lang": "",
        "needs_rag": False,
        "retrieval_decision": "",
        "retrieved_docs": [],
        "saved_memory": False,
        "remembered_context": "",
        "tool_results": "",
        "messages": [],
    }


def _is_new_thread(config: dict) -> bool:
    """True when the thread has no message history yet (first turn).

    Fail-open: if the check itself errors (e.g. the Neon wake race — the
    same transient OperationalError the invoke loop below retries for),
    assume the thread is NOT new. Skipping title generation is harmless;
    re-titling an existing conversation is not.
    """
    try:
        snapshot = run_with_retry(agent.get_state, config)
        values = getattr(snapshot, "values", None) or {}
        return not values.get("messages")
    except Exception:
        logger.warning("Thread state check failed — skipping title generation", exc_info=True)
        return False


# Neon autosuspends an idle compute and kills its connections. The pool
# reconnects on checkout, but the *first* query on a fresh connection can
# still abort while the compute is waking (the pool's ping races the wake).
# Retrying a transient OperationalError absorbs that — the failure in the
# traceback is the checkpointer's very first read, before any node runs, so
# a retry is a clean restart (LangGraph resumes from the checkpoint).
_MAX_DB_RETRIES = 2
_RETRY_DELAY_SECONDS = 0.5


async def run_agent(
    req: AgentRequest,
    ocr_text: str = "",
) -> AgentResponse:

    start_time = time.monotonic()

    initial_state = _build_initial_state(req, ocr_text)

    # One thread per conversation. Defaults to patient_id so older clients
    # (and pre-sidebar data) keep resuming the single per-patient thread.
    thread_id = req.thread_id or req.patient_id

    # recursion_limit is LangGraph's own graph-level safety net. The
    # decoupled pipeline is linear (router -> tools? -> biomistral -> END),
    # so it stays well under this, but the cap guards against any future
    # cyclic edge misbehaving.
    config = {
        "configurable": {
            "thread_id": thread_id,
        },
        "recursion_limit": 15,
    }

    logger.info(
        "Agent request started | thread=%s | OCR=%s",
        thread_id,
        "yes" if ocr_text else "no",
    )

    # Sidebar title: generated once, on the thread's first turn, BEFORE the
    # graph runs so it lands in the initial state — every checkpoint of the
    # conversation then carries it in channel_values, which is where
    # conversation_service reads it back from. Costs one extra LLM call on
    # the first message only; subsequent turns skip this entirely.
    if await run_in_threadpool(_is_new_thread, config):
        initial_state["thread_title"] = await generate_thread_title(req.query)
        logger.info("Thread titled | thread=%s | title=%s", thread_id, initial_state["thread_title"])

    for attempt in range(_MAX_DB_RETRIES + 1):

        try:
            logger.info(
                "Running agent graph | attempt %d/%d",
                attempt + 1,
                _MAX_DB_RETRIES + 1,
            )

            result = await run_in_threadpool(
                agent.invoke,
                initial_state,
                config,
            )

            break

        except psycopg.OperationalError as e:

            if attempt >= _MAX_DB_RETRIES:
                logger.exception(
                    "Agent failed after %d attempts",
                    attempt + 1,
                )
                raise

            logger.warning(
                "Temporary database error | attempt %d/%d | retrying...",
                attempt + 1,
                _MAX_DB_RETRIES + 1,
            )

            await asyncio.sleep(_RETRY_DELAY_SECONDS)

        except Exception:
            logger.exception("Agent graph execution failed")
            raise

    elapsed = time.monotonic() - start_time

    logger.info(
        "Agent request finished in %.2fs | RAG=%s | memory=%s",
        elapsed,
        result.get("needs_rag", False),
        result.get("saved_memory", False),
    )

    return AgentResponse(
        answer=result["final_response"],
        detected_lang=result["detected_lang"],
        needs_rag=result.get("needs_rag", False),
        retrieval_decision=result.get("retrieval_decision") or None,
        sources=[
            d.get("source")
            for d in result.get("retrieved_docs", [])[:3]
            if d.get("source")
        ],
        save_memory=result.get("saved_memory", False),
    )