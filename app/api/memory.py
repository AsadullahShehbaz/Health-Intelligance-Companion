from fastapi import APIRouter, Depends, HTTPException, status
from starlette.concurrency import run_in_threadpool

from app.deps import get_current_user
from app.models.user import User
from app.schemas.memory import (
    CategorizedMemoriesResponse,
    MemoryItemResponse,
    MemoryUpdateRequest,
)
from app.services.memory_service import get_patient_memories_sequenced, update_patient_memory

router = APIRouter(prefix="/memory", tags=["Memory"])


@router.get("/patient/{patient_id}", response_model=CategorizedMemoriesResponse)
async def get_patient_memories(patient_id: str, current_user: User = Depends(get_current_user)):
    if patient_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return await run_in_threadpool(get_patient_memories_sequenced, patient_id)


@router.patch("/patient/{patient_id}/{memory_id}", response_model=MemoryItemResponse)
async def patch_patient_memory(
    patient_id: str,
    memory_id: str,
    body: MemoryUpdateRequest,
    current_user: User = Depends(get_current_user),
):
    if patient_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    updates = body.model_dump(exclude_unset=True)
    updated = await run_in_threadpool(update_patient_memory, patient_id, memory_id, updates)

    if not updated:
        raise HTTPException(status_code=404, detail="Memory record not found")

    return updated
