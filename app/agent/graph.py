# app/agent/graph.py
import time

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition

from app.agent.state import AgentState
from app.agent.nodes.ocr_node import ocr_node
from app.agent.nodes.translate_node import translate_in_node, translate_out_node
from app.agent.nodes.agent_node import agent_node
from app.agent.tools import TOOLS
from app.db.lifespan import checkpointer, store
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


_tool_node = ToolNode(TOOLS)


def _run_tools(state: AgentState) -> AgentState:
    """Execute the tool calls in the newest AIMessage (LangGraph's prebuilt node).

    ToolNode is a Runnable, not a plain function, so it can't be called
    directly from the _logged wrapper — invoke it through its .invoke API.
    Returns {"messages": [...]} which the add_messages reducer merges in.
    """
    return _tool_node.invoke(state)


def _route_after_agent(state: AgentState) -> str:
    route = "tools" if tools_condition(state) == "tools" else "translate_out"
    logger.info("routing after agent -> %s", route)
    return route


def build_health_agent():
    graph = StateGraph(AgentState)

    graph.add_node("ocr", _logged("ocr")(ocr_node))                    # reused unchanged
    graph.add_node("translate_in", _logged("translate_in")(translate_in_node))   # reused unchanged
    graph.add_node("agent", _logged("agent")(agent_node))
    graph.add_node("tools", _logged("tools")(_run_tools))
    graph.add_node("translate_out", _logged("translate_out")(translate_out_node))  # reused unchanged

    graph.set_entry_point("ocr")
    graph.add_edge("ocr", "translate_in")
    graph.add_edge("translate_in", "agent")
    graph.add_conditional_edges("agent", _route_after_agent, {"tools": "tools", "translate_out": "translate_out"})
    graph.add_edge("tools", "agent")
    graph.add_edge("translate_out", END)

    compiled = graph.compile(checkpointer=checkpointer, store=store)
    logger.info("Health agent graph compiled (5 nodes)")
    return compiled