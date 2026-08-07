# app/agent/nodes/facts_node.py
from app.agent.state import AgentState
from app.db.store import store


def fetch_facts_node(state: AgentState) -> AgentState:
    namespace = ("patient_facts", state["patient_id"])
    items = store.search(namespace, query=state["english_query"], limit=5)
    state["patient_facts"] = [item.value for item in items]
    return state