from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(..., min_length=1)


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int = Field(default=1024, gt=0)