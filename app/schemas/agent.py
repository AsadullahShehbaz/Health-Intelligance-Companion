# app/schemas/agent.py
from pydantic import BaseModel, Field
from typing import Optional, Literal


class ToolCall(BaseModel):
    """Grammar-constrained agent decision. Kept deliberately small (5 fixed
    actions, flat action_input dict) — a 7B model reasons about this far
    more reliably than a deep/nested schema."""
    thought: str = Field(..., description="Brief reasoning for this step")
    action: Literal[
        "fetch_patient_facts",
        "retrieve_medical_knowledge",
        "save_patient_fact",
        "save_emotional_state",
        "final_answer",
    ]
    action_input: dict = Field(default_factory=dict)
    answer: Optional[str] = Field(None, description="Required when action is final_answer")


class AgentRequest(BaseModel):
    patient_id: str
    query: str = ""
    image_base64: Optional[str] = None
    # LangGraph thread id — one per conversation. Defaults to patient_id for
    # backwards compatibility with clients that predate the sidebar, so old
    # requests keep resuming the single per-patient thread they always had.
    thread_id: Optional[str] = None


class AgentResponse(BaseModel):
    answer: str
    detected_lang: str
    needs_rag: bool
    retrieval_decision: Optional[str] = None
    sources: list[str] = []
    save_memory: bool


# ── Conversation history (sidebar) ──────────────────────────────────────
# Reconstructed directly from the LangGraph checkpointer — there is no
# separate conversation table. See app/services/conversation_service.py.


class ConversationMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None
    meta: Optional[dict] = None  # mirrors the in-session meta chips (lang, rag, sources)


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