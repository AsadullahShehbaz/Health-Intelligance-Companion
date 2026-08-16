# app/tests/test_remember_node.py
"""Unit tests for the Remember node.

Tests the Remember node's ability to extract new memories, deduplicate against
existing ones, and write only genuinely new items to the store.  Phase 1 adds:
category tagging, severity/onset fields, and categorized output formatting.
"""
import pytest
from unittest.mock import patch
from types import SimpleNamespace

from app.agent.nodes.remember_node import remember_node, _format_existing
from app.agent.state import AgentState
from app.agent.memory_schema import (
    MemoryCategory,
    MemoryDecision,
    MemoryItem,
)


# ── helpers ───────────────────────────────────────────────────────────────────

def _store_dict(text, category="identity", status="active", severity=None, onset=None):
    """Build the dict that remember_node persists via store.put."""
    return {"text": text, "category": category, "status": status,
            "severity": severity, "onset": onset}


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_state_with_memory():
    """Factory for ``AgentState`` dicts including remembered_context."""

    def _make(**kwargs):
        base = {
            "patient_id": "test-patient-01",
            "ocr_context": "",
            "tool_results": "",
            "messages": [],
            "answer": "",
            "final_response": "",
            "raw_input": "What is diabetes?",
            "detected_lang": "en",
            "needs_rag": False,
            "retrieval_decision": "",
            "retrieved_docs": [],
            "saved_memory": False,
            "remembered_context": "",
        }
        base.update(kwargs)
        return base

    return _make


# ── existing tests (adapted for Phase 1 schema) ──────────────────────────────

@pytest.mark.unit
def test_remember_node_writes_new_fact(fake_store, sample_state_with_memory):
    """First message about a new symptom → store.put called once, saved_memory=True."""
    with patch("app.agent.nodes.remember_node.store", fake_store):
        with patch("app.agent.nodes.remember_node._memory_llm") as mock_llm:
            mock_llm.invoke.return_value = MemoryDecision(
                should_write=True,
                memories=[
                    MemoryItem(
                        text="Patient has a persistent headache",
                        category=MemoryCategory.SYMPTOM,
                        status="active",
                        severity="moderate",
                        onset="3 days ago",
                        is_new=True,
                    ),
                ],
            )

            state = sample_state_with_memory(raw_input="I have had a headache for 3 days")
            result = remember_node(state)

            assert mock_llm.invoke.called
            assert len(fake_store._data.get(("patient_memories", "test-patient-01"), {})) == 1
            assert result["saved_memory"] is True
            assert "Patient has a persistent headache" in result["remembered_context"]


@pytest.mark.unit
def test_remember_node_skips_duplicate(fake_store, sample_state_with_memory):
    """Message restating an existing fact → no store.put call, saved_memory=False."""
    fake_store.put(
        ("patient_memories", "test-patient-01"),
        "existing-1",
        {"data": _store_dict("Patient has diabetes", category="symptom")},
    )

    with patch("app.agent.nodes.remember_node.store", fake_store):
        with patch("app.agent.nodes.remember_node._memory_llm") as mock_llm:
            mock_llm.invoke.return_value = MemoryDecision(
                should_write=True,
                memories=[
                    MemoryItem(
                        text="Patient has diabetes",
                        category=MemoryCategory.SYMPTOM,
                        status="active",
                        is_new=False,
                    ),
                ],
            )

            state = sample_state_with_memory(raw_input="Yes, I have diabetes")
            result = remember_node(state)

            assert mock_llm.invoke.called
            assert len(fake_store._data.get(("patient_memories", "test-patient-01"), {})) == 1
            assert result["saved_memory"] is False
            assert "Patient has diabetes" in result["remembered_context"]


@pytest.mark.unit
def test_remember_node_handles_empty_input(fake_store, sample_state_with_memory):
    """Empty raw_input → returns existing context unchanged, no LLM call."""
    fake_store.put(
        ("patient_memories", "test-patient-01"),
        "existing-1",
        {"data": _store_dict("Patient is 28 years old", category="identity")},
    )

    with patch("app.agent.nodes.remember_node.store", fake_store):
        with patch("app.agent.nodes.remember_node._memory_llm") as mock_llm:
            state = sample_state_with_memory(raw_input="")
            result = remember_node(state)

            assert not mock_llm.invoke.called
            assert result["saved_memory"] is False
            assert "Patient is 28 years old" in result["remembered_context"]


@pytest.mark.unit
def test_remember_node_fails_open_on_llm_error(fake_store, sample_state_with_memory):
    """Mock LLM error → node returns existing context, doesn't propagate the exception."""
    fake_store.put(
        ("patient_memories", "test-patient-01"),
        "existing-1",
        {"data": _store_dict("Patient has hypertension", category="symptom")},
    )

    with patch("app.agent.nodes.remember_node.store", fake_store):
        with patch("app.agent.nodes.remember_node._memory_llm") as mock_llm:
            mock_llm.invoke.side_effect = RuntimeError("LLM service unavailable")

            state = sample_state_with_memory(raw_input="I feel dizzy")
            result = remember_node(state)

            assert result["saved_memory"] is False
            assert "Patient has hypertension" in result["remembered_context"]


@pytest.mark.unit
def test_remember_node_fails_open_on_store_unavailable(sample_state_with_memory):
    """store=None → returns empty context, no crash."""
    with patch("app.agent.nodes.remember_node.store", None):
        state = sample_state_with_memory(raw_input="I have a fever")
        result = remember_node(state)

        assert result["saved_memory"] is False
        assert result["remembered_context"] == ""


# ── Phase 1 new tests ────────────────────────────────────────────────────────

@pytest.mark.unit
def test_format_existing_groups_by_category():
    """Memories across categories should appear under separate section headings."""
    memories = [
        _store_dict("Ayan Ahmed, 11th semester CS student, Lahore", "identity"),
        _store_dict("Persistent headache", "symptom", severity="moderate", onset="3 days ago"),
        _store_dict("Panadol 500mg twice daily", "medication", onset="2 days ago"),
        _store_dict("Sleeps ~5hrs/night, skips breakfast", "lifestyle"),
        _store_dict("Mild anxiety about exams", "emotional", onset="2 days ago"),
        _store_dict("Sore throat", "symptom", status="resolved"),
    ]
    result = _format_existing(memories)

    assert "IDENTITY:" in result
    assert "ACTIVE SYMPTOMS:" in result
    assert "MEDICATIONS:" in result
    assert "LIFESTYLE:" in result
    assert "EMOTIONAL STATE:" in result
    assert "RESOLVED HISTORY:" in result
    # Resolved symptom should NOT appear in ACTIVE SYMPTOMS
    lines = result.split("\n")
    symptom_line = next(l for l in lines if "ACTIVE SYMPTOMS" in l)
    assert "Sore throat" not in symptom_line


@pytest.mark.unit
def test_format_existing_includes_severity_onset():
    """Severity and onset should appear in parens after the symptom text."""
    memories = [
        _store_dict("Persistent headache", "symptom", severity="moderate", onset="3 days ago"),
    ]
    result = _format_existing(memories)

    assert "(3 days ago, moderate)" in result


@pytest.mark.unit
def test_format_existing_empty():
    """Empty list → '(empty)'."""
    assert _format_existing([]) == "(empty)"


@pytest.mark.unit
def test_remember_node_stores_full_category_fields(fake_store, sample_state_with_memory):
    """New memories should persist category, status, severity, and onset."""
    with patch("app.agent.nodes.remember_node.store", fake_store):
        with patch("app.agent.nodes.remember_node._memory_llm") as mock_llm:
            mock_llm.invoke.return_value = MemoryDecision(
                should_write=True,
                memories=[
                    MemoryItem(
                        text="Patient has a fever",
                        category=MemoryCategory.SYMPTOM,
                        status="active",
                        severity="mild",
                        onset="yesterday",
                        is_new=True,
                    ),
                ],
            )

            state = sample_state_with_memory(raw_input="I have a mild fever since yesterday")
            remember_node(state)

            # Inspect the stored dict
            stored_items = list(
                fake_store._data[("patient_memories", "test-patient-01")].values()
            )
            assert len(stored_items) == 1
            data = stored_items[0]["data"]
            assert data["category"] == "symptom"
            assert data["status"] == "active"
            assert data["severity"] == "mild"
            assert data["onset"] == "yesterday"


@pytest.mark.unit
def test_remember_node_back_compat_flat_string(fake_store, sample_state_with_memory):
    """Old flat-string memories (no category) are promoted to identity/active."""
    # Simulate an old-format store entry (just a string, not a dict)
    fake_store.put(
        ("patient_memories", "test-patient-01"),
        "old-key",
        {"data": "Patient has diabetes"},
    )

    with patch("app.agent.nodes.remember_node.store", fake_store):
        with patch("app.agent.nodes.remember_node._memory_llm") as mock_llm:
            state = sample_state_with_memory(raw_input="")
            result = remember_node(state)

            # The old fact should still appear in context
            assert "Patient has diabetes" in result["remembered_context"]


@pytest.mark.unit
def test_mixed_categories_all_appear(fake_store, sample_state_with_memory):
    """A fixture patient with mixed categories should have all categories in output."""
    with patch("app.agent.nodes.remember_node.store", fake_store):
        with patch("app.agent.nodes.remember_node._memory_llm") as mock_llm:
            mock_llm.invoke.return_value = MemoryDecision(
                should_write=True,
                memories=[
                    MemoryItem(
                        text="Patient is a 25-year-old software engineer",
                        category=MemoryCategory.IDENTITY,
                        status="active",
                        is_new=True,
                    ),
                    MemoryItem(
                        text="Headache worsening over 3 days",
                        category=MemoryCategory.SYMPTOM,
                        status="active",
                        severity="moderate",
                        onset="3 days ago",
                        is_new=True,
                    ),
                    MemoryItem(
                        text="Takes Paracetamol 500mg as needed",
                        category=MemoryCategory.MEDICATION,
                        status="active",
                        is_new=True,
                    ),
                    MemoryItem(
                        text="Reports stress from work deadlines",
                        category=MemoryCategory.EMOTIONAL,
                        status="active",
                        is_new=True,
                    ),
                ],
            )

            state = sample_state_with_memory(raw_input="I'm 25, work as a software engineer. I've had a worsening headache for 3 days. I take Paracetamol 500mg. Work has been stressful.")
            result = remember_node(state)

            ctx = result["remembered_context"]
            assert "IDENTITY:" in ctx
            assert "ACTIVE SYMPTOMS:" in ctx
            assert "MEDICATIONS:" in ctx
            assert "EMOTIONAL STATE:" in ctx
            assert result["saved_memory"] is True
