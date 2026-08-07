# app/schemas/agent.py
from pydantic import BaseModel, Field
from typing import Optional


class RouterDecision(BaseModel):
    """Structured output contract for the Router Agent. Its JSON schema
    is compiled directly into a llama.cpp grammar, so the model is
    physically constrained to only ever emit this shape."""
    needs_rag: bool = Field(..., description="True if the query needs factual medical lookup")
    save_memory: bool = Field(..., description="True if this message is worth remembering")


class SymptomFact(BaseModel):
    """Structured output contract for the Extraction Agent. Like
    RouterDecision, its JSON schema is compiled into a grammar so the model
    can only ever emit a fact that validates against this shape."""
    has_fact: bool = Field(..., description="True if the message reports a symptom or medical fact worth remembering")
    symptom: Optional[str] = Field(None, description="The symptom or condition mentioned, e.g. 'fever'")
    onset: Optional[str] = Field(None, description="When it started, e.g. 'today', '3 days ago', or a date if stated")
    status: Optional[str] = Field(None, description="ongoing, resolved, or worsening, if mentioned")


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