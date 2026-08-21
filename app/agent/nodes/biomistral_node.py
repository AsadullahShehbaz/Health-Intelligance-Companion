"""Node 3 — Chat.

Receives the raw user input along with any plain-text context the RAG/router's
tools gathered this turn (memory + RAG) and produces the final empathetic
answer from the local GGUF model. Because tool-calling is offloaded to the
router, this node does a single clean inference turn with no JSON or
function-calling overhead.
"""
import time
from typing import List

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from app.agent.nodes.prompts import BIOMISTRAL_PROMPT
from app.agent.state import AgentState
from app.core.llm import llm
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

# OCR documents can be long; cap what we feed the local model so we don't
# blow its context window.
_OCR_CHAR_LIMIT = 2000

# Cap how many prior Human/AI turns we feed the local model so a long
# thread doesn't blow the GGUF context window.
_CHAT_HISTORY_TURN_CAP = 10


def _clean_and_alternate_messages(messages: List[BaseMessage]) -> List[BaseMessage]:
    """Ensures strict role alternation (System -> Human -> AI -> Human...) required by

    Mistral/BioMistral Jinja templates. Merges consecutive messages of the same type.
    """
    if not messages:
        return []

    # Separate system messages from conversational history
    system_msgs = [m for m in messages if isinstance(m, SystemMessage)]
    conv_msgs = [m for m in messages if isinstance(m, (HumanMessage, AIMessage))]

    if not conv_msgs:
        return system_msgs

    # Merge consecutive messages of the exact same role (e.g., Human + Human)
    merged_conv: List[BaseMessage] = []
    for msg in conv_msgs:
        if not merged_conv:
            merged_conv.append(msg)
            continue

        prev_msg = merged_conv[-1]

        # Check if current and previous messages share the same role
        if type(msg) is type(prev_msg):
            prev_text = prev_msg.content if isinstance(prev_msg.content, str) else str(prev_msg.content)
            curr_text = msg.content if isinstance(msg.content, str) else str(msg.content)
            
            # Combine content if it's not duplicate text
            if curr_text and curr_text not in prev_text:
                combined_text = f"{prev_text}\n\n{curr_text}".strip()
            else:
                combined_text = prev_text

            if isinstance(prev_msg, HumanMessage):
                merged_conv[-1] = HumanMessage(content=combined_text)
            elif isinstance(prev_msg, AIMessage):
                merged_conv[-1] = AIMessage(content=combined_text)
        else:
            merged_conv.append(msg)

    # Mistral requires the conversation sequence to start with a HumanMessage after system prompt
    if merged_conv and isinstance(merged_conv[0], AIMessage):
        merged_conv.pop(0)

    # Reconstruct final list: SystemMessage first, followed by strict alternating chat sequence
    return system_msgs + merged_conv


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

    messages: List[BaseMessage] = [SystemMessage(content=formatted_system)]

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

    # Append current question if it isn't already the last human message
    if not messages or not isinstance(messages[-1], HumanMessage) or messages[-1].content != user_question:
        if user_question:
            messages.append(HumanMessage(content=user_question))

    # Clean and merge message sequence to prevent Jinja role template errors
    clean_messages = _clean_and_alternate_messages(messages)

    logger.info(
        "Chat (BioMistral) invoked with %d messages | patient=%s",
        len(clean_messages),
        state["patient_id"],
    )

    logger.info("BioMistral invoked with messages: %s", str(clean_messages)[:200])

    start = time.monotonic()
    response = llm.invoke(clean_messages)
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