# app/agent/state.py
from typing import TypedDict, Optional, Annotated
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    patient_id: str
    raw_input: str
    has_image: bool
    image_base64: Optional[str]

    # Kept separate from raw_input/english_query so the agent never reprocesses
    # ~900 chars of document noise. Only the agent prompt consumes it.
    ocr_context: str

    detected_lang: str
    english_query: str

    # answer is what the unchanged translate_out_node reads; final_response is
    # its translation (or the identity for English) and is what the sidebar's
    # turn-end checkpoint filter keys on being non-empty.
    answer: str
    final_response: str

    # RAG status — repopulated by agent_node from the tool messages that this
    # turn actually used, so the sidebar meta chips and /agent/invoke response
    # keep their existing shape.
    needs_rag: bool
    retrieval_decision: str
    retrieved_docs: list[dict]
    saved_memory: bool   # per-turn: a memory tool ran THIS turn (not a prior one)

    messages: Annotated[list, add_messages]
    tool_results: str
    tool_call_count: int   # loop guard, prevents an unbounded agent<->tools loop