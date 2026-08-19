# app/agent/nodes/biomistral_node.py
"""Node 3 — Chat.

Receives the raw user input along with any plain-text context the RAG/router's
tools gathered this turn (memory + RAG) and produces the final empathetic
answer from the local GGUF model. Because tool-calling is offloaded to the
router, this node does a single clean inference turn with no JSON or
function-calling overhead.
"""
import time

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.agent.state import AgentState
from app.agent.nodes.prompts import BIOMISTRAL_PROMPT
from app.core.llm import llm
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

# OCR documents can be long; cap what we feed the local model so we don't
# blow its context window.
_OCR_CHAR_LIMIT = 2000

# Cap how many prior Human/AI turns we feed the local model so a long
# thread doesn't blow the GGUF context window.
_CHAT_HISTORY_TURN_CAP = 10


def biomistral_node(state: AgentState) -> dict:
    logger.info("▶ Chat Node Started")

    ocr_raw = (state.get("ocr_context") or "")[:_OCR_CHAR_LIMIT]
    ocr_str = f"OCR Document Context:\n{ocr_raw}" if ocr_raw else "No OCR text attached."

    tool_str = state.get("tool_results") or "No external context retrieved."
    remembered = state.get("remembered_context") or "(no known patient history yet)"

    formatted_system = BIOMISTRAL_PROMPT.format(
        ocr_context=ocr_str,
        tool_context=tool_str,
        patient_memory=remembered,
    )

    user_question = (state.get("raw_input") or "").strip()

    messages = [SystemMessage(content=formatted_system)]

    prior_messages = state.get("messages", [])
    chat_history = [
        m for m in prior_messages
        if isinstance(m, HumanMessage)
        or (isinstance(m, AIMessage) and not getattr(m, "tool_calls", None))
    ]

    max_history = _CHAT_HISTORY_TURN_CAP * 2
    if len(chat_history) > max_history:
        chat_history = chat_history[-max_history:]

    messages.extend(chat_history)

    if not messages or not isinstance(messages[-1], HumanMessage) or messages[-1].content != user_question:
        messages.append(HumanMessage(content=user_question))

    logger.info(
        "Chat (BioMistral) invoked with %d messages | patient=%s",
        len(messages),
        state["patient_id"],
    )

    logger.info(f"BioMistral invoked with messages: {messages}")

    start = time.monotonic()
    response = llm.invoke(messages)
    logger.info("✓ BioMistral completed in %.2fs", time.monotonic() - start)

    answer_text = (response.content or "").strip()
    if not answer_text:
        answer_text = (
            "I'm sorry, I wasn't able to generate a proper response to that. "
            "Could you try rephrasing your message?"
        )
        response = AIMessage(content=answer_text)

    logger.info(
        "✓ Chat (BioMistral) produced final answer | patient=%s | chars=%d",
        state["patient_id"],
        len(answer_text),
    )

    logger.info(f"BioMistral produced final answer: {answer_text}")

    return {
        "answer": answer_text,
        "final_response": answer_text,
        "messages": [response],
    }
