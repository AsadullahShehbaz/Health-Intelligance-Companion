# app/agent/graph.py
import time

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import AIMessage

from app.agent.state import AgentState
from app.agent.nodes.agent_node import agent_node
from app.agent.tools import TOOLS
from app.db.lifespan import checkpointer, store
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


def _logged(node_name: str):
    """Wrap a graph node with simple start, finish, and error logs."""

    def decorator(node):
        def wrapped(state: AgentState) -> AgentState:
            start = time.monotonic()

            logger.info("▶ %s node started", node_name)

            try:
                result = node(state)

            except Exception:
                logger.exception("✗ %s node failed", node_name)
                raise

            elapsed = time.monotonic() - start
            logger.info("✓ %s node finished in %.2fs", node_name, elapsed)

            return result

        return wrapped

    return decorator


_tool_node = ToolNode(TOOLS)


def _run_tools(state: AgentState) -> AgentState:
    """Execute tool calls and log only the important details."""

    messages = state.get("messages", [])

    # Show which tools the agent wants to use
    if messages:
        last_message = messages[-1]

        if (
            isinstance(last_message, AIMessage)
            and getattr(last_message, "tool_calls", None)
        ):
            for tool_call in last_message.tool_calls:
                tool_name = tool_call.get("name", "unknown_tool")
                logger.info("🔧 Running tool: %s", tool_name)

    start = time.monotonic()

    try:
        result = _tool_node.invoke(state)

    except Exception:
        logger.exception("✗ Tool execution failed")
        raise

    logger.info(
        "✓ Tools finished in %.2fs",
        time.monotonic() - start,
    )

    return result


def _route_after_agent(state: AgentState) -> str:
    # If the agent requested a tool, continue to the tools node.
    # Otherwise, the agent has produced the final answer.
    route = "tools" if tools_condition(state) == "tools" else END

    logger.info("↪ Agent routing → %s", route)

    return route


def build_health_agent():
    graph = StateGraph(AgentState)

    graph.add_node("agent", _logged("agent")(agent_node))
    graph.add_node("tools", _logged("tools")(_run_tools))

    graph.set_entry_point("agent")

    graph.add_conditional_edges(
        "agent",
        _route_after_agent,
        {
            "tools": "tools",
            END: END,
        },
    )

    graph.add_edge("tools", "agent")

    compiled = graph.compile(
        checkpointer=checkpointer,
        store=store,
    )

    logger.info("✓ Health agent graph compiled")

    return compiled