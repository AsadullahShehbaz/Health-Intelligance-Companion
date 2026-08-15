# app/tests/test_remember_node.py
"""Unit tests for the Remember node.

Tests the Remember node's ability to extract new memories, deduplicate against
existing ones, and write only genuinely new items to the store.
"""
import pytest
from unittest.mock import MagicMock, patch
from types import SimpleNamespace

from app.agent.nodes.remember_node import remember_node
from app.agent.state import AgentState
from app.agent.memory_schema import MemoryDecision, MemoryItem


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


@pytest.mark.unit
def test_remember_node_writes_new_fact(fake_store, sample_state_with_memory):
    """First message about a new symptom → store.put called once, saved_memory=True."""
    with patch("app.agent.nodes.remember_node.store", fake_store):
        with patch("app.agent.nodes.remember_node._memory_llm") as mock_llm:
            # Mock the LLM to return a new memory
            mock_llm.invoke.return_value = MemoryDecision(
                should_write=True,
                memories=[
                    MemoryItem(text="Patient has a persistent headache", is_new=True),
                ],
            )

            state = sample_state_with_memory(raw_input="I have had a headache for 3 days")
            result = remember_node(state)

            # Verify the node called the LLM
            assert mock_llm.invoke.called

            # Verify the store was written to
            stored = fake_store.get(("patient_memories", "test-patient-01"), "")
            # Note: actual key is UUID, so we check _data directly
            assert len(fake_store._data.get(("patient_memories", "test-patient-01"), {})) == 1

            # Verify the result has saved_memory=True
            assert result["saved_memory"] is True

            # Verify remembered_context includes the new fact
            assert "Patient has a persistent headache" in result["remembered_context"]


@pytest.mark.unit
def test_remember_node_skips_duplicate(fake_store, sample_state_with_memory):
    """Message restating an existing fact → no store.put call, saved_memory=False."""
    # Pre-populate the store with an existing memory
    fake_store.put(
        ("patient_memories", "test-patient-01"),
        "existing-1",
        {"data": "Patient has diabetes"},
    )

    with patch("app.agent.nodes.remember_node.store", fake_store):
        with patch("app.agent.nodes.remember_node._memory_llm") as mock_llm:
            # Mock the LLM to return a duplicate (is_new=False)
            mock_llm.invoke.return_value = MemoryDecision(
                should_write=True,
                memories=[
                    MemoryItem(text="Patient has diabetes", is_new=False),
                ],
            )

            state = sample_state_with_memory(raw_input="Yes, I have diabetes")
            result = remember_node(state)

            # Verify the node called the LLM
            assert mock_llm.invoke.called

            # Verify no new store entries were added beyond the existing one
            assert len(fake_store._data.get(("patient_memories", "test-patient-01"), {})) == 1

            # Verify saved_memory=False (no new memories written)
            assert result["saved_memory"] is False

            # Verify remembered_context includes the existing fact
            assert "Patient has diabetes" in result["remembered_context"]


@pytest.mark.unit
def test_remember_node_handles_empty_input(fake_store, sample_state_with_memory):
    """Empty raw_input → returns existing context unchanged, no LLM call."""
    # Pre-populate the store with an existing memory
    fake_store.put(
        ("patient_memories", "test-patient-01"),
        "existing-1",
        {"data": "Patient is 28 years old"},
    )

    with patch("app.agent.nodes.remember_node.store", fake_store):
        with patch("app.agent.nodes.remember_node._memory_llm") as mock_llm:
            state = sample_state_with_memory(raw_input="")
            result = remember_node(state)

            # Verify the LLM was NOT called
            assert not mock_llm.invoke.called

            # Verify saved_memory=False
            assert result["saved_memory"] is False

            # Verify remembered_context has the existing fact
            assert "Patient is 28 years old" in result["remembered_context"]


@pytest.mark.unit
def test_remember_node_fails_open_on_llm_error(fake_store, sample_state_with_memory):
    """Mock LLM error → node returns existing context, doesn't propagate the exception."""
    # Pre-populate the store with an existing memory
    fake_store.put(
        ("patient_memories", "test-patient-01"),
        "existing-1",
        {"data": "Patient has hypertension"},
    )

    with patch("app.agent.nodes.remember_node.store", fake_store):
        with patch("app.agent.nodes.remember_node._memory_llm") as mock_llm:
            # Mock the LLM to raise an exception
            mock_llm.invoke.side_effect = RuntimeError("LLM service unavailable")

            state = sample_state_with_memory(raw_input="I feel dizzy")
            result = remember_node(state)

            # Verify the exception was NOT propagated — the node failed open
            # and returned gracefully

            # Verify saved_memory=False (no memories written due to error)
            assert result["saved_memory"] is False

            # Verify remembered_context has the existing fact (fell back to DB)
            assert "Patient has hypertension" in result["remembered_context"]


@pytest.mark.unit
def test_remember_node_fails_open_on_store_unavailable(sample_state_with_memory):
    """store=None → returns empty context, no crash."""
    with patch("app.agent.nodes.remember_node.store", None):
        state = sample_state_with_memory(raw_input="I have a fever")
        result = remember_node(state)

        # Verify the node didn't crash
        # Verify saved_memory=False
        assert result["saved_memory"] is False

        # Verify remembered_context is empty
        assert result["remembered_context"] == ""
