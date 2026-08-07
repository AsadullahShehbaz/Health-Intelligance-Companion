# app/agent/nodes/rag_node.py
from app.agent.state import AgentState
from app.core.rag.corrective_rag import corrective_retrieve


def rag_node(state: AgentState) -> AgentState:
    query = state.get("rewritten_query") or state["english_query"]
    result = corrective_retrieve(query)
    state["retrieved_docs"] = result["docs"]
    state["retrieval_decision"] = result["decision"]
    return state