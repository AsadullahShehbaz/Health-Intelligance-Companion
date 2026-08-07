# app/agent/graph.py
from langgraph.graph import StateGraph, END

from app.agent.state import AgentState
from app.agent.nodes.ocr_node import ocr_node
from app.agent.nodes.translate_node import translate_in_node, translate_out_node
from app.agent.nodes.router_node import router_node
from app.agent.nodes.facts_node import fetch_facts_node
from app.agent.nodes.rewriter_node import query_rewriter_node
from app.agent.nodes.rag_node import rag_node
from app.agent.nodes.reasoner_node import reasoner_node
from app.agent.nodes.extraction_node import extraction_node
from app.db.checkpointer import checkpointer
from app.db.store import store


def _route_after_router(state: AgentState) -> str:
    return "rewrite" if state["needs_rag"] else "reasoner"


def build_health_agent():
    graph = StateGraph(AgentState)

    graph.add_node("ocr", ocr_node)
    graph.add_node("translate_in", translate_in_node)
    graph.add_node("router", router_node)
    graph.add_node("fetch_facts", fetch_facts_node)
    graph.add_node("rewrite", query_rewriter_node)
    graph.add_node("rag", rag_node)
    graph.add_node("reasoner", reasoner_node)
    graph.add_node("extract_facts", extraction_node)
    graph.add_node("translate_out", translate_out_node)

    graph.set_entry_point("ocr")
    graph.add_edge("ocr", "translate_in")
    graph.add_edge("translate_in", "router")
    graph.add_edge("router", "fetch_facts")
    graph.add_conditional_edges(
        "fetch_facts", _route_after_router, {"rewrite": "rewrite", "reasoner": "reasoner"}
    )
    graph.add_edge("rewrite", "rag")
    graph.add_edge("rag", "reasoner")
    graph.add_edge("reasoner", "extract_facts")
    graph.add_edge("extract_facts", "translate_out")
    graph.add_edge("translate_out", END)

    # Compiling with the checkpointer + store gives automatic conversation
    # continuity per thread_id and persistent per-patient fact memory,
    # replacing the old manual get_memory/save_memory nodes.
    return graph.compile(checkpointer=checkpointer, store=store)