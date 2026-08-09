# app/agent/nodes/facts_node.py
from app.agent.state import AgentState
from app.db.store import store
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


def fetch_facts_node(state: AgentState) -> AgentState:
    namespace = ("patient_facts", state["patient_id"])

    logger.info(
        "fetch_facts | patient=%s | query_len=%d",
        state["patient_id"],
        len(state["english_query"]),
    )

    items = store.search(namespace, query=state["english_query"], limit=5)
    state["patient_facts"] = [item.value for item in items]

    logger.info("fetch_facts | retrieved %d patient facts", len(state["patient_facts"]))
    return state