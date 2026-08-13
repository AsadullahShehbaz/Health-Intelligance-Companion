# app/agent/state.py
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    patient_id: str
    ocr_context: str
    tool_call_count: int   # loop guard, prevents an unbounded agent<->tools loop
    messages: Annotated[list, add_messages]

    # Kept only because app/services/conversation_service.py reads these
    # fields straight out of the checkpoint rows to build the sidebar.
    # Don't rename these without updating that file too.
    raw_input: str
    final_response: str
    detected_lang: str
    needs_rag: bool
    retrieval_decision: str
    retrieved_docs: list[dict]