# app/agent/graph.py
"""Decoupled router-node pipeline.

    Router (Groq, tool-calling)  ──tools?──▶  Tools  ──▶  BioMistral (local GGUF)  ──▶  END
                        │
                        └───── no tools ─────────────────▶  BioMistral  ──▶  END

The router decides whether tools are needed and emits tool_calls; it never
writes the final answer. Tool results are flattened into plain text and
handed to the BioMistral node, which does a single clean inference turn.
"""
import re
import time

from langchain_core.messages import AIMessage
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from app.agent.nodes.biomistral_node import biomistral_node
from app.agent.nodes.router_node import router_node
from app.agent.state import AgentState
from app.agent.tools import TOOLS
from app.db.lifespan import checkpointer, store
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

_tool_node = ToolNode(TOOLS)


def _extract_tool_metadata(tool_messages: list) -> dict:
    """Flatten this turn's ToolMessages into plain text for BioMistral and
    pull out the per-turn metadata flags the sidebar / response schema need.

    Only the *new* tool messages (returned by the ToolNode this turn) are
    scanned, so needs_rag / saved_memory reflect the current turn, not the
    accumulated history.
    """
    extracted: list[str] = []
    rag_used = False
    saved_memory = False
    sources: list[str] = []

    for msg in tool_messages:
        name = getattr(msg, "name", "") or ""
        content = msg.content or ""

        extracted.append(f"--- Context from tool [{name}] ---\n{content}\n")

        if name in ("retrieve_medical_knowledge", "search_web_medical"):
            rag_used = True
            # Parse source titles from formatted tool outputs
            for line in content.splitlines():
                match = re.match(r"^\s*\[([^\]]+)\]", line)
                if match:
                    sources.append(match.group(1))

        if name in ("save_patient_fact", "save_emotional_state"):
            saved_memory = True

    return {
        "tool_results": "\n".join(extracted),
        "needs_rag": rag_used,
        "retrieval_decision": "retrieved" if rag_used else "",
        "retrieved_docs": [{"source": s} for s in sources[:3]],
        "saved_memory": saved_memory,
    }


def _run_tools(state: AgentState) -> dict:
    """Execute the router's tool calls, then fold the results into the
    plain-text context + metadata BioMistral consumes."""
    messages = state.get("messages", [])

    if messages:
        last_message = messages[-1]
        if isinstance(last_message, AIMessage) and getattr(last_message, "tool_calls", None):
            for tool_call in last_message.tool_calls:
                tool_name = tool_call.get("name", "unknown_tool")
                logger.info("🔧 Running tool: %s", tool_name)

    start = time.monotonic()
    try:
        result = _tool_node.invoke(state)
    except Exception:
        logger.exception("✗ Tool execution failed")
        raise
    logger.info("✓ Tools finished in %.2fs", time.monotonic() - start)

    new_tool_msgs = [
        m for m in result.get("messages", []) if getattr(m, "type", None) == "tool"
    ]
    result.update(_extract_tool_metadata(new_tool_msgs))
    return result


def _route_after_router(state: AgentState) -> str:
    """tools_condition wrapper: route to 'tools' when the router emitted
    tool_calls, otherwise straight to the BioMistral reasoning node.

    tools_condition raises on an empty message list; the router always
    persists at least the user's HumanMessage before this runs, but we guard
    the empty case so a unit call can't crash the graph.
    """
    if not state.get("messages"):
        route = "biomistral"
    else:
        route = "tools" if tools_condition(state) == "tools" else "biomistral"
    logger.info("↪ Router routing → %s", route)
    return route


def build_health_agent():
    graph = StateGraph(AgentState)

    # 1. Add nodes
    graph.add_node("router", router_node)
    graph.add_node("tools", _run_tools)
    graph.add_node("biomistral", biomistral_node)

    # 2. Entry point
    graph.set_entry_point("router")

    # 3. Conditional routing from the router
    graph.add_conditional_edges(
        "router",
        _route_after_router,
        {
            "tools": "tools",        # router outputted tool_calls
            "biomistral": "biomistral",  # no tools → straight to reasoning
        },
    )

    # 4. Tools feed their context into BioMistral
    graph.add_edge("tools", "biomistral")

    # 5. BioMistral ends the turn
    graph.add_edge("biomistral", END)

    compiled = graph.compile(
        checkpointer=checkpointer,
        store=store,
    )

    logger.info("✓ Health agent graph compiled (router → tools? → biomistral → END)")
    return compiled
