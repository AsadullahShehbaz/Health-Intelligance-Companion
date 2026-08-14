# app/agent/nodes/biomistral_node.py
"""Node 2 — BioMistral reasoning.

Receives the raw user input along with any plain-text context the router's
tools gathered this turn (memory + RAG) and produces the final empathetic
answer from the local GGUF model. Because tool-calling is offloaded to the
router, this node does a single clean inference turn with no JSON or
function-calling overhead.
"""
import time

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.agent.state import AgentState
from app.core.llm import llm
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

# OCR documents can be long; cap what we feed the local model so we don't
# blow its context window.
_OCR_CHAR_LIMIT = 2000

BIOMISTRAL_PROMPT = """You are an empathetic Pakistani AI health companion.

Use the provided medical & patient context below (if available) to answer the user's health concerns.


{ocr_context}

{tool_context}


GUIDELINES:
- If the query is plain conversational/greeting, reply naturally in plain text.
- If it is a medical query, respond conversationally based on the context. You can recommend these things where helpful:
  - Possible diagnosis or insights
  - Lifestyle adjustments, diet, and exercise suggestions
  - Home care or general advice
  - Clear advice on when to consult a doctor
- Never invent facts outside the provided context.
- When patient facts (e.g., name, age, history) are retrieved from tools, you MUST explicitly reference them in your final response when answering the user.
"""


def biomistral_node(state: AgentState) -> dict:
    logger.info("▶ BioMistral Reasoning Node Started")

    ocr_raw = (state.get("ocr_context") or "")[:_OCR_CHAR_LIMIT]
    ocr_str = f"OCR Document Context:\n{ocr_raw}" if ocr_raw else "No OCR text attached."

    tool_str = state.get("tool_results") or "No external context retrieved."

    formatted_system = BIOMISTRAL_PROMPT.format(
        ocr_context=ocr_str,
        tool_context=tool_str,
    )

    # Single clean inference turn: system prompt (with gathered context) +
    # the user's raw input only. The router already persisted the user
    # message, so here we store just the final AIMessage — completing the
    # conversation pair without re-inserting the HumanMessage.
    messages = [
        SystemMessage(content=formatted_system),
        HumanMessage(content=state["raw_input"]),
    ]

    logger.info(
        "BioMistral invoked with %d messages | patient=%s",
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
        "✓ BioMistral produced final answer | patient=%s | chars=%d",
        state["patient_id"],
        len(answer_text),
    )

    logger.info(f"BioMistral produced final answer: {answer_text}")

    return {
        "answer": answer_text,
        "final_response": answer_text,
        "messages": [response],
    }
