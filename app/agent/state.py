# app/agent/state.py
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    patient_id: str
    ocr_context: str
    tool_results: str      # plain text gathered from tools this turn, shown to BioMistral
    raw_input: str
    messages: Annotated[list, add_messages]

    # NEW — populated by remember_node, consumed by biomistral_node
    remembered_context: str   # formatted "- fact\n- fact" block, always present

    # Metadata flags — read straight from checkpoint rows by
    # conversation_service.py to build the sidebar. Don't rename these
    # without updating that file too.
    needs_rag: bool
    retrieval_decision: str
    retrieved_docs: list[dict]
    saved_memory: bool     # per-turn: a memory tool ran THIS turn (not a prior one)
    detected_lang: str     # kept for conversation_service / agent_service (legacy)

    # answer/final_response are the same text right now (Phase 2 removed the
    # translate_out node that used to translate answer -> final_response).
    # Kept as two separate keys so a future translation phase can reintroduce
    # that split without touching conversation_service.py.
    answer: str
    final_response: str
