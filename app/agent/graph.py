# app/agent/graph.py
import time

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition

from app.agent.state import AgentState
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
    """Execute the tool calls in the newest AIMessage (LangGraph's prebuilt node)."""
    return _tool_node.invoke(state)


def _route_after_agent(state: AgentState) -> str:
    # tools_condition looks at the last message: if it has tool_calls, go to
    # "tools"; otherwise the agent gave a final answer, so end the turn.
    route = "tools" if tools_condition(state) == "tools" else END
    logger.info("routing after agent -> %s", route)
    return route


def build_health_agent():
    graph = StateGraph(AgentState)

    graph.add_node("agent", _logged("agent")(agent_node))
    graph.add_node("tools", _logged("tools")(_run_tools))
    
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", _route_after_agent, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")

    compiled = graph.compile(checkpointer=checkpointer, store=store)
    logger.info("Health agent graph compiled (2 nodes)")
    return compiled