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


# ── Phase 3: OCR ingestion tests ─────────────────────────────────────────────

@pytest.mark.unit
def test_remember_node_extracts_facts_from_ocr(fake_store, sample_state_with_memory):
    """OCR'd prescription text → medication facts extracted and persisted."""
    with patch("app.agent.nodes.remember_node.store", fake_store):
        with patch("app.agent.nodes.remember_node._memory_llm") as mock_llm:
            mock_llm.invoke.return_value = MemoryDecision(
                should_write=True,
                memories=[
                    MemoryItem(
                        text="Prescribed Panadol 500mg twice daily",
                        category=MemoryCategory.MEDICATION,
                        status="active",
                        is_new=True,
                    ),
                    MemoryItem(
                        text="CBC report: hemoglobin 10.5 g/dL (below reference range)",
                        category=MemoryCategory.LAB_RESULT,
                        status="active",
                        is_new=True,
                    ),
                ],
            )

            ocr_text = "Rx: Panadol 500mg BD x 5 days\nLab: Hb 10.5 g/dL (low)"
            state = sample_state_with_memory(
                raw_input="Here is my prescription and lab report",
                ocr_context=ocr_text,
            )
            result = remember_node(state)

            # LLM was invoked and OCR facts persisted
            assert mock_llm.invoke.called
            assert result["saved_memory"] is True

            # Verify the system prompt included the OCR text
            system_msg = mock_llm.invoke.call_args[0][0][0]
            assert "Panadol 500mg" in system_msg.content
            assert "Hb 10.5" in system_msg.content
            assert "DOCUMENT TEXT" in system_msg.content

            # Verify persisted facts carry the right categories
            stored = list(
                fake_store._data[("patient_memories", "test-patient-01")].values()
            )
            assert len(stored) == 2
            categories = {s["data"]["category"] for s in stored}
            assert categories == {"medication", "lab_result"}

            # Categories should appear in the formatted context
            assert "MEDICATIONS:" in result["remembered_context"]
            assert "LAB RESULTS:" in result["remembered_context"]


@pytest.mark.unit
def test_remember_node_ocr_only_no_text_message(fake_store, sample_state_with_memory):
    """Image uploaded with no accompanying text → extraction still runs on OCR alone."""
    with patch("app.agent.nodes.remember_node.store", fake_store):
        with patch("app.agent.nodes.remember_node._memory_llm") as mock_llm:
            mock_llm.invoke.return_value = MemoryDecision(
                should_write=True,
                memories=[
                    MemoryItem(
                        text="Blood glucose fasting: 132 mg/dL",
                        category=MemoryCategory.LAB_RESULT,
                        status="active",
                        is_new=True,
                    ),
                ],
            )

            state = sample_state_with_memory(
                raw_input="",
                ocr_context="Fasting blood sugar: 132 mg/dL",
            )
            result = remember_node(state)

            # LLM should still have been called (OCR present)
            assert mock_llm.invoke.called

            # The user turn should be non-empty (placeholder)
            user_msg = mock_llm.invoke.call_args[0][0][1]
            assert user_msg["content"] != ""

            # The lab fact should be persisted and surfaced
            assert result["saved_memory"] is True
            assert "LAB RESULTS:" in result["remembered_context"]
            assert "132 mg/dL" in result["remembered_context"]


@pytest.mark.unit
def test_remember_node_no_ocr_no_text_skips_llm(fake_store, sample_state_with_memory):
    """Neither text nor OCR → no LLM call, existing context returned."""
    fake_store.put(
        ("patient_memories", "test-patient-01"),
        "existing-1",
        {"data": _store_dict("Patient is 28 years old", category="identity")},
    )

    with patch("app.agent.nodes.remember_node.store", fake_store):
        with patch("app.agent.nodes.remember_node._memory_llm") as mock_llm:
            state = sample_state_with_memory(raw_input="", ocr_context="")
            result = remember_node(state)

            assert not mock_llm.invoke.called
            assert result["saved_memory"] is False
            assert "Patient is 28 years old" in result["remembered_context"]


@pytest.mark.unit
def test_remember_node_no_ocr_block_when_empty(fake_store, sample_state_with_memory):
    """No OCR attached → the system prompt should not contain the DOCUMENT TEXT block."""
    with patch("app.agent.nodes.remember_node.store", fake_store):
        with patch("app.agent.nodes.remember_node._memory_llm") as mock_llm:
            mock_llm.invoke.return_value = MemoryDecision(
                should_write=False, memories=[],
            )

            state = sample_state_with_memory(raw_input="hello", ocr_context="")
            remember_node(state)

            system_msg = mock_llm.invoke.call_args[0][0][0]
            assert "DOCUMENT TEXT" not in system_msg.content


@pytest.mark.unit
def test_remember_node_ocr_duplicate_not_rewritten(fake_store, sample_state_with_memory):
    """OCR fact already known → is_new=False → nothing written."""
    fake_store.put(
        ("patient_memories", "test-patient-01"),
        "existing-1",
        {"data": _store_dict("Prescribed Panadol 500mg twice daily", category="medication")},
    )

    with patch("app.agent.nodes.remember_node.store", fake_store):
        with patch("app.agent.nodes.remember_node._memory_llm") as mock_llm:
            mock_llm.invoke.return_value = MemoryDecision(
                should_write=True,
                memories=[
                    MemoryItem(
                        text="Prescribed Panadol 500mg twice daily",
                        category=MemoryCategory.MEDICATION,
                        status="active",
                        is_new=False,
                    ),
                ],
            )

            state = sample_state_with_memory(
                raw_input="same prescription again",
                ocr_context="Rx: Panadol 500mg BD",
            )
            result = remember_node(state)

            # No new rows
            assert len(fake_store._data[("patient_memories", "test-patient-01")]) == 1
            assert result["saved_memory"] is False
            # But the existing fact still shows up in context
            assert "Panadol" in result["remembered_context"]


# ── Phase 2: fact lifecycle / supersession tests ──────────────────────────────

@pytest.mark.unit
def test_supersession_resolves_symptom(fake_store, sample_state_with_memory):
    """'My headache is gone' → the existing headache record flips to resolved
    in place; no duplicate row; BioMistral sees it under RESOLVED HISTORY."""
    fake_store.put(
        ("patient_memories", "test-patient-01"),
        "headache-key",
        {"data": _store_dict(
            "Patient has a persistent headache", "symptom",
            severity="moderate", onset="3 days ago",
        )},
    )

    with patch("app.agent.nodes.remember_node.store", fake_store):
        with patch("app.agent.nodes.remember_node._memory_llm") as mock_llm:
            mock_llm.invoke.return_value = MemoryDecision(
                should_write=True,
                memories=[
                    MemoryItem(
                        text="Patient's headache has resolved",
                        category=MemoryCategory.SYMPTOM,
                        status="resolved",
                        supersedes_id="headache-key",
                        is_new=True,
                    ),
                ],
            )

            state = sample_state_with_memory(raw_input="My headache is gone now")
            result = remember_node(state)

            # Still exactly one row — updated, not duplicated
            rows = fake_store._data[("patient_memories", "test-patient-01")]
            assert len(rows) == 1
            assert "headache-key" in rows

            # The record itself now says resolved with the new text
            data = rows["headache-key"]["data"]
            assert data["status"] == "resolved"
            assert data["text"] == "Patient's headache has resolved"

            # The change counts as a save for the UI flag
            assert result["saved_memory"] is True

            # Downstream context: resolved, not active
            ctx = result["remembered_context"]
            assert "RESOLVED HISTORY:" in ctx
            active_line = next(
                (l for l in ctx.split("\n") if "ACTIVE SYMPTOMS" in l), ""
            )
            assert active_line == ""  # no active symptoms section at all


@pytest.mark.unit
def test_supersession_updates_severity(fake_store, sample_state_with_memory):
    """'Headache getting worse' → same row updated to severe, still active."""
    fake_store.put(
        ("patient_memories", "test-patient-01"),
        "headache-key",
        {"data": _store_dict(
            "Patient has a persistent headache", "symptom",
            severity="moderate", onset="3 days ago",
        )},
    )

    with patch("app.agent.nodes.remember_node.store", fake_store):
        with patch("app.agent.nodes.remember_node._memory_llm") as mock_llm:
            mock_llm.invoke.return_value = MemoryDecision(
                should_write=True,
                memories=[
                    MemoryItem(
                        text="Patient's headache is worsening",
                        category=MemoryCategory.SYMPTOM,
                        status="active",
                        severity="severe",
                        onset="3 days ago",
                        supersedes_id="headache-key",
                        is_new=True,
                    ),
                ],
            )

            state = sample_state_with_memory(raw_input="My headache is getting worse")
            result = remember_node(state)

            rows = fake_store._data[("patient_memories", "test-patient-01")]
            assert len(rows) == 1

            data = rows["headache-key"]["data"]
            assert data["severity"] == "severe"
            assert data["status"] == "active"
            assert data["text"] == "Patient's headache is worsening"

            # Still surfaced as an active symptom, now with severe
            assert "ACTIVE SYMPTOMS:" in result["remembered_context"]
            assert "severe" in result["remembered_context"]


@pytest.mark.unit
def test_supersession_missing_key_falls_back_to_new_write(fake_store, sample_state_with_memory):
    """Hallucinated supersedes_id → graceful fallback: write as a new fact."""
    with patch("app.agent.nodes.remember_node.store", fake_store):
        with patch("app.agent.nodes.remember_node._memory_llm") as mock_llm:
            mock_llm.invoke.return_value = MemoryDecision(
                should_write=True,
                memories=[
                    MemoryItem(
                        text="Patient's headache has resolved",
                        category=MemoryCategory.SYMPTOM,
                        status="resolved",
                        supersedes_id="does-not-exist",
                        is_new=True,
                    ),
                ],
            )

            state = sample_state_with_memory(raw_input="My headache is gone")
            result = remember_node(state)

            # A new row was written under a fresh key instead
            rows = fake_store._data[("patient_memories", "test-patient-01")]
            assert len(rows) == 1
            assert "does-not-exist" not in rows
            assert result["saved_memory"] is True


@pytest.mark.unit
def test_extraction_prompt_shows_keys_not_downstream(fake_store, sample_state_with_memory):
    """The extraction LLM sees [key] references; BioMistral's context does not."""
    fake_store.put(
        ("patient_memories", "test-patient-01"),
        "headache-key",
        {"data": _store_dict("Patient has a persistent headache", "symptom")},
    )

    with patch("app.agent.nodes.remember_node.store", fake_store):
        with patch("app.agent.nodes.remember_node._memory_llm") as mock_llm:
            mock_llm.invoke.return_value = MemoryDecision(
                should_write=False, memories=[],
            )

            state = sample_state_with_memory(raw_input="hello")
            result = remember_node(state)

            # Extraction prompt: keyed format
            system_msg = mock_llm.invoke.call_args[0][0][0]
            assert "[headache-key]" in system_msg.content

            # Downstream context: clean, no keys
            assert "[headache-key]" not in result["remembered_context"]
            assert "headache-key" not in result["remembered_context"]


@pytest.mark.unit
def test_supersession_and_new_fact_same_turn(fake_store, sample_state_with_memory):
    """One turn can both update an existing fact and add a brand-new one."""
    fake_store.put(
        ("patient_memories", "test-patient-01"),
        "headache-key",
        {"data": _store_dict("Patient has a persistent headache", "symptom",
                             severity="moderate")},
    )

    with patch("app.agent.nodes.remember_node.store", fake_store):
        with patch("app.agent.nodes.remember_node._memory_llm") as mock_llm:
            mock_llm.invoke.return_value = MemoryDecision(
                should_write=True,
                memories=[
                    MemoryItem(
                        text="Patient's headache has resolved",
                        category=MemoryCategory.SYMPTOM,
                        status="resolved",
                        supersedes_id="headache-key",
                        is_new=True,
                    ),
                    MemoryItem(
                        text="Patient started feeling mild nausea",
                        category=MemoryCategory.SYMPTOM,
                        status="active",
                        severity="mild",
                        is_new=True,
                    ),
                ],
            )

            state = sample_state_with_memory(
                raw_input="Headache is gone but I feel nauseous now"
            )
            result = remember_node(state)

            # One updated row + one new row
            rows = fake_store._data[("patient_memories", "test-patient-01")]
            assert len(rows) == 2
            assert rows["headache-key"]["data"]["status"] == "resolved"

            ctx = result["remembered_context"]
            assert "RESOLVED HISTORY:" in ctx
            assert "ACTIVE SYMPTOMS:" in ctx
            assert "nausea" in ctx
            assert result["saved_memory"] is True
