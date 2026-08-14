# app/services/conversation_service.py
"""Conversation history for the sidebar, backed directly by the LangGraph
checkpointer.

There is deliberately no separate conversation table — the checkpointer is
the source of truth. Every completed agent turn writes a checkpoint whose
`channel_values.final_response` is non-empty, so a conversation is exactly
the chronological sequence of those turn-end checkpoints for a thread.

Queries share the checkpointer's psycopg pool (app/db/pool.py), which is
tuned for Neon: it pings on checkout, reconnects after idle drops, and holds
real sessions on the direct endpoint.
"""
import time

import psycopg
from psycopg.rows import dict_row

from app.db.lifespan import checkpointer
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

# A turn is "complete" once its final_response is set. The graph writes an
# intermediate checkpoint after every superstep, but those carry an empty
# final_response — filtering on it leaves exactly one row per finished turn.
_TURN_END = (
    "checkpoint_ns = ''"
    " AND (checkpoint->'channel_values'->>'final_response') IS NOT NULL"
    " AND (checkpoint->'channel_values'->>'final_response') <> ''"
)

# Fields we need per turn. Selecting only these (rather than the whole
# channel_values dict) keeps image_base64 blobs out of the result set.
_TURN_FIELDS = """
    thread_id,
    checkpoint_id,
    checkpoint->'channel_values'->>'raw_input'         AS raw_input,
    checkpoint->'channel_values'->>'final_response'    AS final_response,
    checkpoint->'channel_values'->>'detected_lang'     AS detected_lang,
    checkpoint->'channel_values'->>'retrieval_decision' AS retrieval_decision,
    (checkpoint->'channel_values'->>'needs_rag')::boolean AS needs_rag,
    checkpoint->'channel_values'->'retrieved_docs'     AS retrieved_docs,
    checkpoint->>'ts'                                  AS ts
"""

# Neon autosuspends an idle compute and kills its connections. The pool
# reconnects on checkout, but the *first* query on a fresh connection can
# still abort while the compute is waking — the same race agent_service.py
# retries for, so absorb it here too.
_MAX_DB_RETRIES = 1
_RETRY_DELAY_SECONDS = 0.5


def _query(sql: str, params: list) -> list[dict]:
    def run() -> list[dict]:
        with checkpointer.conn.connection() as conn:
            cur = conn.cursor(row_factory=dict_row)
            cur.execute(sql, params)
            return cur.fetchall()

    for attempt in range(_MAX_DB_RETRIES + 1):
        try:
            return run()
        except psycopg.OperationalError:
            if attempt >= _MAX_DB_RETRIES:
                logger.exception(
                    "Checkpoint query failed after %d attempts | params=%s",
                    attempt + 1,
                    params,
                )
                raise
            logger.warning(
                "Transient DB error in checkpoint query (attempt %d/%d), retrying...",
                attempt + 1,
                _MAX_DB_RETRIES + 1,
            )
            time.sleep(_RETRY_DELAY_SECONDS)


def _fetch_turns(patient_id: str, thread_id: str | None = None) -> list[dict]:
    """Chronological turn-end checkpoints for a patient, optionally one thread."""
    logger.info(
        "Fetching turns | patient=%s | thread=%s",
        patient_id,
        thread_id or "(all)",
    )
    sql = (
        f"SELECT {_TURN_FIELDS}"
        f" FROM checkpoints WHERE {_TURN_END}"
        " AND (checkpoint->'channel_values'->>'patient_id') = %s"
    )
    params: list = [patient_id]
    if thread_id is not None:
        sql += " AND thread_id = %s"
        params.append(thread_id)
    sql += " ORDER BY thread_id ASC, checkpoint_id ASC"
    turns = _query(sql, params)
    logger.info("Fetched %d turns | patient=%s", len(turns), patient_id)
    return turns


def _title(turns: list[dict]) -> str:
    """Conversation title = first user message; the sidebar truncates it."""
    for t in turns:
        if t["raw_input"] and t["raw_input"].strip():
            return t["raw_input"].strip()
    return "Untitled conversation"


def _sources(turn: dict) -> list[str]:
    return [
        d["source"]
        for d in (turn["retrieved_docs"] or [])
        if isinstance(d, dict) and d.get("source")
    ][:3]


def list_conversations(patient_id: str) -> list[dict]:
    """Sidebar rows: every conversation the patient has started, newest first."""
    start = time.monotonic()
    grouped: dict[str, list[dict]] = {}
    for t in _fetch_turns(patient_id):
        grouped.setdefault(t["thread_id"], []).append(t)

    conversations = []
    for thread_id, turns in grouped.items():
        turns.sort(key=lambda r: r["checkpoint_id"])  # chronological
        first, last = turns[0], turns[-1]
        conversations.append(
            {
                "thread_id": thread_id,
                "title": _title(turns),
                "updated_at": last["ts"] or "",
                "message_count": len(turns) * 2,
                "snippet": (last["final_response"] or "").strip(),
            }
        )

    # ISO timestamps come from the same source (checkpoint ts), so a plain
    # lexicographic sort is a valid time order.
    conversations.sort(key=lambda c: c["updated_at"], reverse=True)
    logger.info(
        "✓ list_conversations grouped %d turns into %d conversations in %.2fs | patient=%s",
        sum(len(v) for v in grouped.values()),
        len(conversations),
        time.monotonic() - start,
        patient_id,
    )
    return conversations


def get_conversation(thread_id: str, patient_id: str) -> dict | None:
    """Full message transcript for one thread, or None if it isn't the
    patient's (ownership is enforced by the patient_id inside the state)."""
    start = time.monotonic()
    turns = _fetch_turns(patient_id, thread_id)
    if not turns:
        logger.info(
            "No turns found | thread=%s | patient=%s",
            thread_id,
            patient_id,
        )
        return None

    messages = []
    for t in turns:
        raw = (t["raw_input"] or "").strip()
        answer = (t["final_response"] or "").strip()
        if not raw and not answer:
            continue
        messages.append({"role": "user", "content": raw, "timestamp": t["ts"]})
        messages.append(
            {
                "role": "assistant",
                "content": answer,
                "timestamp": t["ts"],
                "meta": {
                    "detected_lang": t["detected_lang"] or "en",
                    "needs_rag": bool(t["needs_rag"]),
                    "retrieval_decision": t["retrieval_decision"],
                    "sources": _sources(t),
                },
            }
        )

    result = {
        "thread_id": thread_id,
        "patient_id": patient_id,
        "title": _title(turns),
        "updated_at": turns[-1]["ts"] or "",
        "messages": messages,
    }
    logger.info(
        "✓ get_conversation built %d messages from %d turns in %.2fs | thread=%s",
        len(messages),
        len(turns),
        time.monotonic() - start,
        thread_id,
    )
    return result
