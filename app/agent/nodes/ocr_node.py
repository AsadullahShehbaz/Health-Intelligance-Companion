# app/agent/nodes/ocr_node.py
from app.agent.state import AgentState
from app.core.rag.ocr import extract_text_from_base64


def ocr_node(state: AgentState) -> AgentState:
    if not state.get("has_image"):
        return state
    extracted = extract_text_from_base64(state["image_base64"])
    if extracted:
        state["raw_input"] = f"{state['raw_input']}\n{extracted}".strip()
    return state