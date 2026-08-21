"""Unit tests for app/services/memory_service.py — sequenced retrieval and updates."""
import pytest
from types import SimpleNamespace

from app.schemas.memory import MemoryCategory
from app.services.memory_service import get_patient_memories_sequenced, update_patient_memory


def _make_store_item(key, data, created_at="2024-01-01T00:00:00", updated_at="2024-01-02T00:00:00"):
    return SimpleNamespace(
        key=key,
        value={"data": data},
        created_at=created_at,
        updated_at=updated_at,
    )


def _fake_store(items):
    class _FakeStore:
        def __init__(self, items):
            self._items = items

        def search(self, namespace, query="", limit=5):
            return self._items[:limit]

        def get(self, namespace, key):
            for item in self._items:
                if item.key == key:
                    return item
            return None

        def put(self, namespace, key, value):
            pass

    return _FakeStore(items)


@pytest.mark.unit
async def test_get_patient_memories_returns_sequenced_categories(monkeypatch):
    items = [
        _make_store_item("k1", {"text": "John Doe", "category": "identity", "status": "active"}),
        _make_store_item("k2", {"text": "Headache", "category": "symptom", "status": "active", "severity": "moderate", "onset": "2 days ago"}),
        _make_store_item("k3", {"text": "Lisinopril", "category": "medication", "status": "active"}),
        _make_store_item("k4", {"text": "Broken leg", "category": "symptom", "status": "resolved"}),
    ]

    fake = _fake_store(items)
    monkeypatch.setattr("app.services.memory_service.store", fake)

    result = get_patient_memories_sequenced("patient-1")
    assert result["patient_id"] == "patient-1"
    assert len(result["categories"]) == 6

    cat_map = {c["category"]: c for c in result["categories"]}
    assert cat_map["identity"]["items"][0]["text"] == "John Doe"
    assert cat_map["symptom"]["items"][0]["text"] == "Headache"
    assert cat_map["symptom"]["items"][0]["severity"] == "moderate"
    assert cat_map["symptom"]["items"][0]["onset"] == "2 days ago"
    assert cat_map["medication"]["items"][0]["text"] == "Lisinopril"
    assert len(cat_map["symptom"]["items"]) == 2
    assert cat_map["lab_result"]["items"] == []
    assert cat_map["lifestyle"]["items"] == []
    assert cat_map["emotional"]["items"] == []


@pytest.mark.unit
async def test_get_patient_memories_empty(monkeypatch):
    fake = _fake_store([])
    monkeypatch.setattr("app.services.memory_service.store", fake)

    result = get_patient_memories_sequenced("patient-1")
    assert result["patient_id"] == "patient-1"
    for cat in result["categories"]:
        assert cat["items"] == []


@pytest.mark.unit
async def test_get_patient_memories_ignores_unknown_categories(monkeypatch):
    items = [
        _make_store_item("k1", {"text": "Unknown fact", "category": "unknown_category", "status": "active"}),
    ]

    fake = _fake_store(items)
    monkeypatch.setattr("app.services.memory_service.store", fake)

    result = get_patient_memories_sequenced("patient-1")
    cat_map = {c["category"]: c for c in result["categories"]}
    for cat in result["categories"]:
        assert cat["items"] == []


@pytest.mark.unit
async def test_patch_patient_memory_updates_record(monkeypatch):
    items = [_make_store_item("mem-1", {"text": "Old text", "category": "symptom", "status": "active"})]
    fake = _fake_store(items)
    monkeypatch.setattr("app.services.memory_service.store", fake)

    updated = update_patient_memory("patient-1", "mem-1", {"text": "New text", "status": "resolved"})
    assert updated is not None
    assert updated["text"] == "New text"
    assert updated["status"] == "resolved"
    assert updated["id"] == "mem-1"


@pytest.mark.unit
async def test_patch_patient_memory_not_found(monkeypatch):
    fake = _fake_store([])
    monkeypatch.setattr("app.services.memory_service.store", fake)

    updated = update_patient_memory("patient-1", "missing-id", {"text": "New text"})
    assert updated is None


@pytest.mark.unit
async def test_patch_patient_memory_partial_update(monkeypatch):
    items = [_make_store_item("mem-1", {"text": "Old text", "category": "symptom", "status": "active", "severity": "mild", "onset": "1 day ago"})]
    fake = _fake_store(items)
    monkeypatch.setattr("app.services.memory_service.store", fake)

    updated = update_patient_memory("patient-1", "mem-1", {"severity": "severe"})
    assert updated is not None
    assert updated["severity"] == "severe"
    assert updated["text"] == "Old text"
    assert updated["status"] == "active"


@pytest.mark.unit
async def test_get_patient_memories_preserves_category_sequence(monkeypatch):
    items = [
        _make_store_item("k1", {"text": "Medication", "category": "medication", "status": "active"}),
        _make_store_item("k2", {"text": "Identity", "category": "identity", "status": "active"}),
        _make_store_item("k3", {"text": "Symptom", "category": "symptom", "status": "active"}),
    ]

    fake = _fake_store(items)
    monkeypatch.setattr("app.services.memory_service.store", fake)

    result = get_patient_memories_sequenced("patient-1")
    categories = [c["category"] for c in result["categories"]]
    assert categories == [
        "identity",
        "symptom",
        "medication",
        "lab_result",
        "lifestyle",
        "emotional",
    ]
