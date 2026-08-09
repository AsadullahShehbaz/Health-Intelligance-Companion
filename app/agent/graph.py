# app/agent/graph.py
import time

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
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


def _logged(node_name: str):
    """Wrap a graph node so its execution lifecycle is logged uniformly.

    Every node runs under a try/except here, so a stack trace is tagged with
    the exact node that failed instead of surfacing as a bare error at the
    graph level. Timings also surface slow LLM/RAG steps.
    """

    def decorator(node):
        def wrapped(state: AgentState) -> AgentState:
            start = time.monotonic()
            logger.info("node=%s started", node_name)
            try:
                result = node(state)
            except Exception:
                logger.exception("node=%s failed", node_name)
                raise
            logger.info(
                "node=%s finished in %.2fs",
                node_name,
                time.monotonic() - start,
            )
            return result

        return wrapped

    return decorator


def _route_after_router(state: AgentState) -> str:
    route = "rewrite" if state["needs_rag"] else "reasoner"
    logger.info(
        "routing after fetch_facts | needs_rag=%s -> next=%s",
        state["needs_rag"],
        route,
    )
    return route


def build_health_agent():
    graph = StateGraph(AgentState)

    graph.add_node("ocr", _logged("ocr")(ocr_node))
    graph.add_node("translate_in", _logged("translate_in")(translate_in_node))
    graph.add_node("router", _logged("router")(router_node))
    graph.add_node("fetch_facts", _logged("fetch_facts")(fetch_facts_node))
    graph.add_node("rewrite", _logged("rewrite")(query_rewriter_node))
    graph.add_node("rag", _logged("rag")(rag_node))
    graph.add_node("reasoner", _logged("reasoner")(reasoner_node))
    graph.add_node("extract_facts", _logged("extract_facts")(extraction_node))
    graph.add_node("translate_out", _logged("translate_out")(translate_out_node))

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
    compiled = graph.compile(checkpointer=checkpointer, store=store)
    logger.info("Health agent graph compiled (9 nodes)")
    return compiled