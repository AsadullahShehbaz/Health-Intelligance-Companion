# app/schemas/agent.py
from pydantic import BaseModel, Field
from typing import Optional


class RouterDecision(BaseModel):
    """Structured output contract for the Router Agent. Its JSON schema
    is compiled directly into a llama.cpp grammar, so the model is
    physically constrained to only ever emit this shape."""
    needs_rag: bool = Field(..., description="True if the query needs factual medical lookup")
    save_memory: bool = Field(..., description="True if this message is worth remembering")


class AgentRequest(BaseModel):
    patient_id: str
    query: str
    image_base64: Optional[str] = None


class AgentResponse(BaseModel):
    answer: str
    detected_lang: str
    needs_rag: bool
    retrieval_decision: Optional[str] = None
    sources: list[str] = []
    save_memory: bool