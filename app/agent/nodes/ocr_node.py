# app/agent/nodes/ocr_node.py
from app.agent.state import AgentState
from app.core.rag.ocr import extract_text_from_base64
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


def ocr_node(state: AgentState) -> AgentState:
    if not state.get("has_image"):
        return state

    logger.info(
        "ocr | image supplied | raw_input_len=%d",
        len(state.get("raw_input", "")),
    )

    extracted = extract_text_from_base64(state["image_base64"])

    if extracted:
        state["ocr_context"] = f"{state['raw_input']}\n{extracted}".strip()
        logger.info("ocr | extracted %d characters of text", len(extracted))
    else:
        logger.warning("ocr | no text extracted from image")

    return state