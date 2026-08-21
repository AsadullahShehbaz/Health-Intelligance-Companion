Here is a clear, step-by-step implementation plan for an AI coding agent to implement the patient historical memory endpoint and frontend dashboard management features.

---

### Phase 1: Backend Data Models & Memory Schemas

#### Step 1.1: Update Schema Definitions (`app/schemas/memory.py`)

Create Pydantic schemas to validate requests/responses for fetching and updating patient memories.

```python
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

class CategorizedMemoriesResponse(BaseModel):
    patient_id: str
    categories: List[dict]  # Contains category_name and items list in sequential order

class MemoryUpdateRequest(BaseModel):
    text: Optional[str] = None
    category: Optional[MemoryCategory] = None
    status: Optional[str] = None
    severity: Optional[str] = None
    onset: Optional[str] = None

```

---

### Phase 2: Memory Service Implementation

#### Step 2.1: Add Store Operations in Memory Service (`app/services/memory_service.py`)

Create a dedicated service layer to retrieve and update records stored in `langgraph.store.postgres` using `run_with_retry`.

```python
from app.db.lifespan import store
from app.db.pool import run_with_retry
from app.agent.memory_schema import MemoryCategory
from app.agent.nodes.remember_node import MEMORY_NAMESPACE, _namespace

CATEGORY_SEQUENCE = [
    MemoryCategory.IDENTITY,
    MemoryCategory.SYMPTOM,
    MemoryCategory.MEDICATION,
    MemoryCategory.LAB_RESULT,
    MemoryCategory.LIFESTYLE,
    MemoryCategory.EMOTIONAL,
]

def get_patient_memories_sequenced(patient_id: str) -> dict:
    items = run_with_retry(store.search, _namespace(patient_id), limit=500)
    
    # Group items by category
    categorized = {cat.value: [] for cat in CATEGORY_SEQUENCE}
    
    for item in items:
        data = item.value.get("data", {})
        if not data:
            continue
        category = data.get("category", MemoryCategory.IDENTITY.value)
        
        memory_dict = {
            "id": item.key,
            "text": data.get("text", ""),
            "category": category,
            "status": data.get("status", "active"),
            "severity": data.get("severity"),
            "onset": data.get("onset"),
            "created_at": str(getattr(item, "created_at", "")),
            "updated_at": str(getattr(item, "updated_at", ""))
        }
        
        if category in categorized:
            categorized[category].append(memory_dict)
        else:
            categorized.setdefault("other", []).append(memory_dict)

    # Format response adhering strictly to CATEGORY_SEQUENCE
    ordered_response = []
    for cat in CATEGORY_SEQUENCE:
        ordered_response.append({
            "category": cat.value,
            "display_name": cat.value.replace("_", " ").title(),
            "items": categorized.get(cat.value, [])
        })

    return {"patient_id": patient_id, "categories": ordered_response}

def update_patient_memory(patient_id: str, memory_id: str, updates: dict) -> dict:
    existing = run_with_retry(store.get, _namespace(patient_id), memory_id)
    if not existing:
        return None
        
    data = dict(existing.value.get("data", {}))
    for key, val in updates.items():
        if val is not None:
            data[key] = val.value if hasattr(val, "value") else val
            
    run_with_retry(store.put, _namespace(patient_id), memory_id, {"data": data})
    data["id"] = memory_id
    return data

```

---

### Phase 3: API Endpoint Implementation

#### Step 3.1: Add Endpoint Router (`app/api/memory.py`)

Implement `GET` and `PATCH` routes for memory interactions protected by `get_current_user`.

```python
from fastapi import APIRouter, Depends, HTTPException, status
from starlette.concurrency import run_in_threadpool
from app.deps import get_current_user
from app.models.user import User
from app.schemas.memory import CategorizedMemoriesResponse, MemoryItemResponse, MemoryUpdateRequest
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
    current_user: User = Depends(get_current_user)
):
    if patient_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
    updates = body.model_dump(exclude_unset=True)
    updated = await run_in_threadpool(update_patient_memory, patient_id, memory_id, updates)
    
    if not updated:
        raise HTTPException(status_code=404, detail="Memory record not found")
        
    return updated

```

#### Step 3.2: Register Router in Main Application (`app/main.py`)

Include the new memory router into the FastAPI app instance.

```python
from app.api import auth, chat, agent, voice, memory  # Add memory

app.include_router(memory.router)

```

---

### Phase 4: Frontend Integration

#### Step 4.1: Extend API Client Utility (`frontend/src/utils/api.js`)

Add API calls for retrieving and updating patient memories.

```javascript
export async function fetchPatientMemories(patientId) {
  const res = await fetch(`/memory/patient/${patientId}`, {
    headers: { Authorization: `Bearer ${getAuthToken()}` }
  });
  if (!res.ok) throw new Error("Failed to load memories");
  return res.json();
}

export async function updatePatientMemory(patientId, memoryId, updateData) {
  const res = await fetch(`/memory/patient/${patientId}/${memoryId}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${getAuthToken()}`
    },
    body: JSON.stringify(updateData)
  });
  if (!res.ok) throw new Error("Failed to update memory");
  return res.json();
}

```

#### Step 4.2: Build Dashboard Memory Management UI (`frontend/src/components/MemoryDashboard.jsx`)

Create a modal or sidebar tab displaying memories grouped in sequential category order with inline editing features.

* **UI Capabilities:**
* Displays sequential sections: **Identity → Symptoms → Medications → Lab Results → Lifestyle → Emotional**.


* Displays badges for `status`, `severity`, and `onset`.


* Provides an **"Edit"** trigger on hover or click for quick updating of text, status, severity, and category.





---

### Verification & Testing Tasks for Agent

1. **Unit Test Backend Endpoints:** Create `tests/api/test_memory.py` using `AsyncClient` to mock user context and test `GET /memory/patient/{id}` and `PATCH /memory/patient/{id}/{memory_id}`.


2. **Sequential Category Verification:** Verify that the output array preserves the standard sequence defined by `MemoryCategory`.


3. **End-to-End Validation:** Run the agent `invoke` loop to verify that edited/updated memories immediately take effect in subsequent `remember_node` runs.