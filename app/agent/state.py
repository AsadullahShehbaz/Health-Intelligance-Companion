# app/agent/state.py
from typing import TypedDict, Optional


class AgentState(TypedDict):
    patient_id: str
    raw_input: str
    has_image: bool
    image_base64: Optional[str]

    detected_lang: str
    english_query: str
    rewritten_query: str

    needs_rag: bool
    save_memory: bool

    retrieved_docs: list[dict]
    retrieval_decision: str

    recent_memory: list[dict]

    patient_facts: list[dict]

    answer: str
    final_response: str