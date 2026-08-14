"""Unit tests for app/agent/nodes/biomistral_node.py.

Covers:
- answer / final_response set from the local model's response
- empty model response → fallback message
- tool_results context is folded into the system prompt
- ocr_context is folded into the system prompt (and truncated)
- only the final AIMessage is stored (the user message is the router's job)
"""
import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.agent.nodes.biomistral_node import _OCR_CHAR_LIMIT, biomistral_node


# ── answer / final_response ──────────────────────────────────────────────────

@pytest.mark.unit
def test_biomistral_sets_answer_from_response(fake_llm, sample_state):
    fake_llm.response_text = "You likely have a common cold."
    fake_llm.tool_calls = None

    state = sample_state(raw_input="I have a runny nose")
    result = biomistral_node(state)

    assert result["answer"] == "You likely have a common cold."
    assert result["final_response"] == "You likely have a common cold."


@pytest.mark.unit
def test_biomistral_empty_response_gets_fallback(fake_llm, sample_state):
    fake_llm.response_text = ""
    fake_llm.tool_calls = None

    state = sample_state()
    result = biomistral_node(state)

    assert "wasn't able to generate" in result["answer"]
    assert result["final_response"] == result["answer"]


@pytest.mark.unit
def test_biomistral_stores_only_final_ai_message(fake_llm, sample_state):
    """The router persists the user message; BioMistral stores only its own
    final AIMessage, completing the conversation pair without duplicating
    the HumanMessage."""
    fake_llm.response_text = "final answer"
    fake_llm.tool_calls = None

    state = sample_state(raw_input="hi")
    result = biomistral_node(state)

    assert len(result["messages"]) == 1
    assert isinstance(result["messages"][0], AIMessage)
    assert result["messages"][0].content == "final answer"


# ── context folding ──────────────────────────────────────────────────────────

def _capture_system(fake_llm):
    """Replace fake_llm.invoke so it records the SystemMessage it receives."""
    captured = {}
    orig = fake_llm.invoke

    def _cap(messages):
        captured["system"] = next(
            (m for m in messages if isinstance(m, SystemMessage)), None
        )
        return orig(messages)

    fake_llm.invoke = _cap
    return captured


@pytest.mark.unit
def test_biomistral_includes_tool_results(fake_llm, sample_state):
    fake_llm.response_text = "ok"
    fake_llm.tool_calls = None
    captured = _capture_system(fake_llm)

    state = sample_state(tool_results="--- Context from tool [retrieve_medical_knowledge] ---\nDiabetes info")
    biomistral_node(state)

    assert captured["system"] is not None
    assert "Diabetes info" in captured["system"].content


@pytest.mark.unit
def test_biomistral_includes_ocr_context(fake_llm, sample_state):
    fake_llm.response_text = "ok"
    fake_llm.tool_calls = None
    captured = _capture_system(fake_llm)

    state = sample_state(ocr_context="Patient: John Doe\nDiagnosis: Hypertension")
    biomistral_node(state)

    assert "Hypertension" in captured["system"].content


@pytest.mark.unit
def test_biomistral_truncates_long_ocr(fake_llm, sample_state):
    fake_llm.response_text = "ok"
    fake_llm.tool_calls = None
    captured = _capture_system(fake_llm)

    long_ocr = "Z" * 5000
    state = sample_state(ocr_context=long_ocr)
    biomistral_node(state)

    # Only _OCR_CHAR_LIMIT chars of the OCR text should reach the prompt.
    assert captured["system"].content.count("Z") <= _OCR_CHAR_LIMIT


@pytest.mark.unit
def test_biomistral_no_context_uses_placeholders(fake_llm, sample_state):
    """With no OCR and no tool results, the prompt carries the 'no context'
    placeholders rather than empty strings."""
    fake_llm.response_text = "ok"
    fake_llm.tool_calls = None
    captured = _capture_system(fake_llm)

    state = sample_state(ocr_context="", tool_results="")
    biomistral_node(state)

    system_text = captured["system"].content
    assert "No OCR text attached." in system_text
    assert "No external context retrieved." in system_text
