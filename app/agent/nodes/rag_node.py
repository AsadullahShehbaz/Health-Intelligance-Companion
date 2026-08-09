# app/agent/nodes/rag_node.py
from app.agent.state import AgentState
from app.core.rag.corrective_rag import corrective_retrieve
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


def rag_node(state: AgentState) -> AgentState:
    query = state.get("rewritten_query") or state["english_query"]

    logger.info("rag | starting corrective retrieval | query=%r", query)

    try:
        result = corrective_retrieve(query)

        state["retrieved_docs"] = result["docs"]
        state["retrieval_decision"] = result["decision"]

        logger.info(
            "rag | decision=%s | avg_score=%s | docs=%d",
            result["decision"],
            result.get("avg_score"),
            len(result["docs"]),
        )
    except Exception:
        # A dead/suspended Qdrant or failed web search must not kill the whole
        # turn — the patient's own document (ocr_context) is often enough to
        # answer. Degrade to no external context; the reasoner still runs.
        logger.exception("rag | retrieval failed; continuing without external docs")
        state["retrieved_docs"] = []
        state["retrieval_decision"] = "failed"

    return state