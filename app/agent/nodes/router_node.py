# app/agent/nodes/router_node.py
"""Node 1 — Router.

A fast Groq model (llama-3.3-70b-versatile) bound with the healthcare tools
decides whether the turn needs any tools (memory / RAG) and emits the
tool_calls when it does. It never produces the final answer — that is the
BioMistral node's job — so on a no-tool turn the router stores only the
user's message (no intermediate assistant text that would pollute history).
"""
import time

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from app.agent.state import AgentState
from app.agent.tools import TOOLS
from app.config import settings
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

# Groq is used strictly for routing / tool-calling — reliable .bind_tools()
# support that the local GGUF model can't do cleanly.
router_llm = ChatGroq(
    api_key=settings.GROQ_API_KEY,
    model_name=settings.GROQ_MODEL,
    temperature=0.0,
).bind_tools(TOOLS)

ROUTER_SYSTEM_PROMPT = """You are an intelligent routing agent for a healthcare assistant.
Your job is to analyze the conversation and call appropriate tools ONLY if required:
1. Call 'fetch_patient_facts' if the user mentions past history/symptoms.
2. Call 'retrieve_medical_knowledge' if the user asks a specific medical/health query.
3. Call 'save_patient_fact' or 'save_emotional_state' if the user reports new symptoms or emotional distress.

If no tools are needed (e.g., greetings, small talk), do NOT call any tools.
Never call the same tool with the same input more than once in a turn.
Patient ID: {patient_id}
"""


def router_node(state: AgentState) -> dict:
    logger.info("▶ Router Node Started | patient=%s", state["patient_id"])

    system_text = ROUTER_SYSTEM_PROMPT.format(patient_id=state["patient_id"])
    messages = [SystemMessage(content=system_text)] + list(state.get("messages", []))

    # The current user input is not in history yet at the start of a turn
    # (the previous turn ended on an assistant message), so append it for
    # this invocation only. It gets persisted to state below.
    if not messages or not isinstance(messages[-1], HumanMessage):
        messages.append(HumanMessage(content=state["raw_input"]))

    start = time.monotonic()
    response = router_llm.invoke(messages)
    logger.info("✓ Router invoke finished in %.2fs", time.monotonic() - start)

    tool_calls = getattr(response, "tool_calls", None)

    # Always persist the user's message so the conversation pair survives in
    # the checkpoint (add_messages appends; losing the HumanMessage breaks
    # role alternation for the local model on later turns). The router's own
    # AIMessage is only stored when it actually carries tool_calls —
    # otherwise it would be a ghost assistant turn before the real answer.
    if tool_calls:
        names = [tc.get("name", "?") for tc in tool_calls]
        logger.info("Router requested tools: %s", ", ".join(names))
        return {"messages": [HumanMessage(content=state["raw_input"]), response]}

    logger.info("Router decided no tools needed → straight to BioMistral")
    return {"messages": [HumanMessage(content=state["raw_input"])]}
