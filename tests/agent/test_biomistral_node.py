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


@pytest.mark.unit
def test_biomistral_includes_remembered_context(fake_llm, sample_state):
    """Patient memory from remember_node should appear in the system prompt."""
    fake_llm.response_text = "ok"
    fake_llm.tool_calls = None
    captured = _capture_system(fake_llm)

    state = sample_state(remembered_context="Patient name: Ayan, Semester: 11th class")
    biomistral_node(state)

    assert captured["system"] is not None
    assert "Ayan" in captured["system"].content


@pytest.mark.unit
def test_biomistral_prompt_has_holistic_reasoning_section(fake_llm, sample_state):
    """The system prompt should instruct the model to cross-reference across
    categorized memory sections (symptoms vs medications vs lifestyle)."""
    fake_llm.response_text = "ok"
    fake_llm.tool_calls = None
    captured = _capture_system(fake_llm)

    # Categorized memory block (as produced by Phase 1's _format_existing)
    categorized_memory = (
        "IDENTITY: Ayan Ahmed, 11th semester CS student, Lahore\n"
        "ACTIVE SYMPTOMS: Persistent headache (3 days ago, moderate)\n"
        "MEDICATIONS: Panadol 500mg twice daily (2 days ago)\n"
        "LIFESTYLE: Sleeps ~5hrs/night, skips breakfast\n"
        "EMOTIONAL STATE: Mild anxiety about exams (2 days ago)\n"
        "RESOLVED HISTORY: Sore throat (resolved, last week)"
    )
    state = sample_state(remembered_context=categorized_memory)
    biomistral_node(state)

    system_text = captured["system"].content

    # The categorized headings should be present
    assert "IDENTITY:" in system_text
    assert "ACTIVE SYMPTOMS:" in system_text
    assert "MEDICATIONS:" in system_text

    # The holistic reasoning instructions should be present
    assert "HOLISTIC REASONING" in system_text
    assert "cross-reference" in system_text


@pytest.mark.unit
def test_biomistral_prompt_cross_references_symptoms_and_meds(fake_llm, sample_state):
    """When patient has both symptoms and medications, the prompt should carry
    both so the model can reason about conflicts."""
    fake_llm.response_text = "ok"
    fake_llm.tool_calls = None
    captured = _capture_system(fake_llm)

    state = sample_state(
        remembered_context=(
            "ACTIVE SYMPTOMS: Fever (2 days ago, mild)\n"
            "MEDICATIONS: Paracetamol 500mg (1 day ago)"
        )
    )
    biomistral_node(state)

    system_text = captured["system"].content
    assert "Fever" in system_text
    assert "Paracetamol" in system_text
    assert "MEDICATIONS" in system_text
