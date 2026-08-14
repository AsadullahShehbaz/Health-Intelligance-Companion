# app/schemas/agent.py
from pydantic import BaseModel, Field
from typing import Optional, Literal


class ToolCall(BaseModel):
    """Grammar-constrained agent decision."""
    thought: str = Field(..., description="Brief reasoning for this step")
    action: Literal[
        "fetch_patient_facts",
        "retrieve_medical_knowledge",
        "save_patient_fact",
        "save_emotional_state",
        "final_answer",
    ]
    action_input: dict = Field(default_factory=dict)
    # Required (no Optional, no default null) so the model can no longer
    # emit "answer": null and skip past our checks. It can still emit ""
    # (an empty string) on a bad generation — we deliberately do NOT add a
    # strict min_length here, because that would make pydantic raise a
    # ValidationError on empty text, which just swaps one generic fallback
    # for another. Instead, agent_node.py checks for blank/short answers
    # itself and does something more useful about it (see agent_node.py).
    answer: str = Field(
        default="",
        description="For final_answer: the full reply text. For any tool action: a short one-line note on why you're calling it.",
    )


class AgentRequest(BaseModel):
    patient_id: str
    query: str = ""
    image_base64: Optional[str] = None
    thread_id: Optional[str] = None


class AgentResponse(BaseModel):
    answer: str
    detected_lang: str
    needs_rag: bool
    retrieval_decision: Optional[str] = None
    sources: list[str] = []
    save_memory: bool


class ConversationMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None
    meta: Optional[dict] = None


class ConversationMeta(BaseModel):
    thread_id: str
    title: str
    updated_at: str
    message_count: int
    snippet: Optional[str] = None


class ConversationDetail(BaseModel):
    thread_id: str
    patient_id: str
    title: str
    updated_at: str
    messages: list[ConversationMessage]