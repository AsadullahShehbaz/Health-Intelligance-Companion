from typing import List, Optional
from pydantic import BaseModel
from app.agent.memory_schema import MemoryCategory


class MemoryItemResponse(BaseModel):
    id: str
    text: str
    category: MemoryCategory
    status: str
    severity: Optional[str] = None
    onset: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class CategoryGroup(BaseModel):
    category: str
    display_name: str
    items: List[MemoryItemResponse]


class CategorizedMemoriesResponse(BaseModel):
    patient_id: str
    categories: List[CategoryGroup]


class MemoryUpdateRequest(BaseModel):
    text: Optional[str] = None
    category: Optional[MemoryCategory] = None
    status: Optional[str] = None
    severity: Optional[str] = None
    onset: Optional[str] = None
