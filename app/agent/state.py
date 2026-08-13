# app/agent/state.py
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    patient_id: str
    ocr_context: str
    tool_call_count: int   # loop guard, prevents an unbounded agent<->tools loop
    tool_results: str      # scratch text built each turn, shown to the LLM in the prompt
    messages: Annotated[list, add_messages]

    # answer/final_response are the same text right now (Phase 2 removed the
    # translate_out node that used to translate answer -> final_response).
    # Kept as two separate keys so a future translation phase can reintroduce
    # that split without touching conversation_service.py.
    answer: str
    final_response: str

    # Kept because app/services/conversation_service.py reads these fields
    # straight out of the checkpoint rows to build the sidebar. Don't rename
    # these without updating that file too.
    raw_input: str
    detected_lang: str
    needs_rag: bool
    retrieval_decision: str
    retrieved_docs: list[dict]
    saved_memory: bool   # per-turn: a memory tool ran THIS turn (not a prior one)