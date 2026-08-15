# app/agent/memory_schema.py
"""Structured-output schema for the Remember node.

Directly ports MemoryItem / MemoryDecision from 14-memory-store.ipynb.
Kept in its own module (not agent/state.py) because these are LLM
structured-output contracts, not graph state.
"""
from typing import List

from pydantic import BaseModel, Field


class MemoryItem(BaseModel):
    text: str = Field(description="Atomic user/patient memory as a short sentence")
    is_new: bool = Field(
        description="True if this memory is NEW and should be stored. "
        "False if it duplicates/overlaps something already known."
    )


class MemoryDecision(BaseModel):
    should_write: bool = Field(description="Whether to store any memories this turn")
    memories: List[MemoryItem] = Field(
        default_factory=list,
        description="Atomic memories extracted from the user's latest message",
    )
