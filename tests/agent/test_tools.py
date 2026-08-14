"""Unit tests for app/agent/tools.py — all four LangGraph tools."""
import pytest

from app.agent.tools import (
    TOOLS,
    fetch_patient_facts,
    retrieve_medical_knowledge,
    save_emotional_state,
    save_patient_fact,
)


# ── TOOLS list ───────────────────────────────────────────────────────────────

@pytest.mark.unit
def test_tools_list_has_four():
    assert len(TOOLS) == 4
    names = {t.name for t in TOOLS}
    assert names == {
        "fetch_patient_facts",
        "retrieve_medical_knowledge",
        "save_patient_fact",
        "save_emotional_state",
    }


# ── fetch_patient_facts ─────────────────────────────────────────────────────

@pytest.mark.unit
def test_fetch_patient_facts_returns_history(monkeypatch, fake_store):
    """With facts in the store, returns formatted history lines."""
    fake_store.put(("patient_facts", "p1"), "key1", {
        "symptom": "fever", "onset": "3 days ago", "status": "ongoing",
    })
    monkeypatch.setattr("app.agent.tools.store", fake_store)

    result = fetch_patient_facts.invoke({"patient_id": "p1", "query": "fever"})
    assert "fever" in result
    assert "Known patient history" in result


@pytest.mark.unit
def test_fetch_patient_facts_no_history(monkeypatch, fake_store):
    """Empty store → 'No relevant patient history found.'"""
    monkeypatch.setattr("app.agent.tools.store", fake_store)
    result = fetch_patient_facts.invoke({"patient_id": "noone", "query": "x"})
    assert "No relevant patient history" in result


@pytest.mark.unit
def test_fetch_patient_facts_store_none(monkeypatch):
    """When store is None → graceful message, no crash."""
    monkeypatch.setattr("app.agent.tools.store", None)
    result = fetch_patient_facts.invoke({"patient_id": "p1", "query": "x"})
    assert "not available" in result.lower()


# ── retrieve_medical_knowledge ──────────────────────────────────────────────

@pytest.mark.unit
def test_retrieve_medical_knowledge_success(monkeypatch, fake_qdrant):
    """With mocked Qdrant returning high-score docs → formatted result."""
    result = retrieve_medical_knowledge.invoke({"query": "diabetes"})
    assert "Retrieval decision" in result
    assert "who.int" in result  # from fake_qdrat canned docs


@pytest.mark.unit
def test_retrieve_medical_knowledge_no_docs(monkeypatch):
    """When retrieve returns empty → 'No relevant documents found.'"""
    monkeypatch.setattr("app.agent.tools.corrective_retrieve", lambda *a, **k: {
        "docs": [], "decision": "incorrect", "avg_score": 0.0,
    })
    result = retrieve_medical_knowledge.invoke({"query": "obscure"})
    assert "No relevant documents" in result


@pytest.mark.unit
def test_retrieve_medical_knowledge_handles_error(monkeypatch):
    """If corrective_retrieve raises → error string, not exception."""
    monkeypatch.setattr(
        "app.agent.tools.corrective_retrieve",
        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    result = retrieve_medical_knowledge.invoke({"query": "x"})
    assert "Error" in result


# ── save_patient_fact ────────────────────────────────────────────────────────

@pytest.mark.unit
def test_save_patient_fact_success(monkeypatch, fake_store):
    monkeypatch.setattr("app.agent.tools.store", fake_store)
    result = save_patient_fact.invoke({
        "patient_id": "p1", "symptom": "headache",
        "onset": "today", "status": "mild",
        "source_message": "I have a headache",
    })
    assert "headache" in result
    # Verify it was persisted
    items = fake_store.search(("patient_facts", "p1"))
    assert any(item.value.get("symptom") == "headache" for item in items)


@pytest.mark.unit
def test_save_patient_fact_store_none(monkeypatch):
    monkeypatch.setattr("app.agent.tools.store", None)
    result = save_patient_fact.invoke({
        "patient_id": "p1", "symptom": "x", "onset": "y",
        "status": "z", "source_message": "m",
    })
    assert "not available" in result.lower()


# ── save_emotional_state ────────────────────────────────────────────────────

@pytest.mark.unit
def test_save_emotional_state_success(monkeypatch, fake_store):
    monkeypatch.setattr("app.agent.tools.store", fake_store)
    result = save_emotional_state.invoke({
        "patient_id": "p1", "emotion": "anxiety",
        "intensity": "high", "trigger": "diagnosis",
        "source_message": "I'm scared",
    })
    assert "anxiety" in result
    items = fake_store.search(("patient_emotions", "p1"))
    assert any(item.value.get("emotion") == "anxiety" for item in items)


@pytest.mark.unit
def test_save_emotional_state_store_none(monkeypatch):
    monkeypatch.setattr("app.agent.tools.store", None)
    result = save_emotional_state.invoke({
        "patient_id": "p1", "emotion": "fear", "intensity": "low",
        "trigger": "x", "source_message": "m",
    })
    assert "not available" in result.lower()
