# app/agent/memory_schema.py
"""Structured-output schema for the Remember node.

Each MemoryItem is now category-tagged so BioMistral can reason over
symptoms separately from lifestyle, medications, etc.  Fields like
status/severity/onset carry the clinical detail the diagnostic prompt
needs — without forcing BioMistral to parse structure out of flat prose.
"""
from enum import Enum
from typing import List, Literal

from pydantic import BaseModel, Field


class MemoryCategory(str, Enum):
    IDENTITY = "identity"          # name, age, occupation, city, family
    SYMPTOM = "symptom"            # medical complaint
    MEDICATION = "medication"      # current/past drugs, dosage
    LAB_RESULT = "lab_result"      # from OCR'd reports
    LIFESTYLE = "lifestyle"        # diet, exercise, sleep, habits
    EMOTIONAL = "emotional"        # mood, stress, anxiety


class MemoryItem(BaseModel):
    text: str = Field(description="Atomic user/patient memory as a short sentence")
    category: MemoryCategory = Field(
        description="Category this memory belongs to (identity, symptom, "
        "medication, lab_result, lifestyle, emotional).",
    )
    status: Literal["active", "resolved", "historical"] = Field(
        default="active",
        description="active = currently true, resolved = no longer applies "
        "(e.g. symptom gone, med stopped), historical = was true in the past.",
    )
    severity: str | None = Field(
        default=None,
        description="Severity level for symptoms (e.g. mild, moderate, severe). "
        "Omit for non-symptom categories.",
    )
    onset: str | None = Field(
        default=None,
        description="When this fact started / was reported (e.g. '3 days ago', "
        "'last week'). Omit if not applicable.",
    )
    supersedes_id: str | None = Field(
        default=None,
        description="Set ONLY when this fact updates/replaces an existing "
        "memory: copy that memory's [key] from CURRENT PATIENT DETAILS "
        "exactly. Otherwise null.",
    )
    is_new: bool = Field(
        description="True if this memory is NEW and should be stored. "
        "False if it duplicates/overlaps something already known.",
    )


class MemoryDecision(BaseModel):
    should_write: bool = Field(description="Whether to store any memories this turn")
    memories: List[MemoryItem] = Field(
        default_factory=list,
        description="Atomic memories extracted from the user's latest message",
    )
