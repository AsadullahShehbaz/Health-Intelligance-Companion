import json
from typing import Any

from app.agent.memory_schema import MemoryCategory
from app.db.lifespan import store
from app.db.pool import run_with_retry

MEMORY_NAMESPACE = "patient_memories"

CATEGORY_SEQUENCE = [
    MemoryCategory.IDENTITY,
    MemoryCategory.SYMPTOM,
    MemoryCategory.MEDICATION,
    MemoryCategory.LAB_RESULT,
    MemoryCategory.LIFESTYLE,
    MemoryCategory.EMOTIONAL,
]


def _namespace(patient_id: str) -> tuple:
    return (MEMORY_NAMESPACE, patient_id)


def _extract_payload(raw_value: Any) -> dict:
    """Safely extracts dictionary payload regardless of raw store value format."""
    val = raw_value

    # Decode JSON string if value was serialized as a string
    if isinstance(val, str):
        try:
            val = json.loads(val)
        except json.JSONDecodeError:
            return {}

    if not isinstance(val, dict):
        return {}

    # Handle both nested {"data": {...}} and flat {...} dictionary formats
    if "data" in val and isinstance(val["data"], dict):
        return val["data"]

    return val


def get_patient_memories_sequenced(patient_id: str) -> dict:
    items = run_with_retry(store.search, _namespace(patient_id), limit=500)

    categorized = {cat.value: [] for cat in CATEGORY_SEQUENCE}

    for item in items:
        data = _extract_payload(item.value)
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
            "updated_at": str(getattr(item, "updated_at", "")),
        }

        if category in categorized:
            categorized[category].append(memory_dict)
        else:
            categorized.setdefault("other", []).append(memory_dict)

    ordered_response = []
    for cat in CATEGORY_SEQUENCE:
        ordered_response.append({
            "category": cat.value,
            "display_name": cat.value.replace("_", " ").title(),
            "items": categorized.get(cat.value, []),
        })

    return {"patient_id": patient_id, "categories": ordered_response}


def update_patient_memory(patient_id: str, memory_id: str, updates: dict) -> dict | None:
    existing = run_with_retry(store.get, _namespace(patient_id), memory_id)
    if not existing:
        return None

    data = dict(_extract_payload(existing.value))
    for key, val in updates.items():
        if val is not None:
            data[key] = val.value if hasattr(val, "value") else val

    run_with_retry(store.put, _namespace(patient_id), memory_id, {"data": data})
    data["id"] = memory_id
    return data