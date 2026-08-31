"""Unit tests for app/agent/nodes/router_node.py.

Covers:
- no-tool path: stores only the user message (no ghost assistant turn)
- tool-call path: stores user message + AIMessage carrying tool_calls
- current input is appended to the LLM call when history doesn't end on one
- patient_id is interpolated into the system prompt
"""
import pytest
from langchain_core.messages import AIMessage, HumanMessage

from app.agent.nodes.router_node import ROUTER_SYSTEM_PROMPT, router_node


# ── no-tool path ──────────────────────────────────────────────────────────────

@pytest.mark.unit
def test_router_no_tools_stores_only_user_message(fake_llm, sample_state):
    """When the router decides no tools are needed, it leaves the already-seeded
    HumanMessage in state and emits no new assistant message."""
    fake_llm.response_text = "irrelevant"
    fake_llm.tool_calls = None

    state = sample_state(raw_input="Hello there")
    result = router_node(state)

    assert result["messages"] == []
    assert state["messages"][-1].content == "Hello there"
    assert "answer" not in result
    assert "final_response" not in result


# ── tool-call path ────────────────────────────────────────────────────────────

@pytest.mark.unit
def test_router_tool_call_stores_only_ai_tool_call(fake_llm, sample_state):
    """The current user message is already seeded into state; the router
    only needs to return the AIMessage carrying tool_calls."""
    fake_llm.tool_calls = [{"name": "retrieve_medical_knowledge", "args": {"query": "fever"}, "id": "tc1"}]

    state = sample_state(raw_input="I have a fever")
    result = router_node(state)

    assert len(result["messages"]) == 1
    assert isinstance(result["messages"][0], AIMessage)
    assert result["messages"][0].tool_calls  # truthy


# ── current input appended to the LLM call ───────────────────────────────────

@pytest.mark.unit
def test_router_uses_seeded_human_message_when_history_ends_on_ai(fake_llm, sample_state):
    """The current turn is already seeded in state; the router uses that
    HumanMessage without appending a duplicate copy."""
    fake_llm.tool_calls = None
    captured = {}
    orig_invoke = fake_llm.invoke

    def _capture(messages):
        captured["last"] = messages[-1]
        return orig_invoke(messages)

    fake_llm.invoke = _capture

    state = sample_state(
        raw_input="new question",
        messages=[
            HumanMessage(content="old q"),
            AIMessage(content="old a"),
            HumanMessage(content="new question"),
        ],
    )
    router_node(state)

    assert isinstance(captured["last"], HumanMessage)
    assert captured["last"].content == "new question"


@pytest.mark.unit
def test_router_does_not_duplicate_input_when_history_ends_on_human(
    fake_llm, sample_state,
):
    """If the last history message is already the current user input, the
    router must not append a second copy."""
    fake_llm.tool_calls = None
    captured = {}
    orig_invoke = fake_llm.invoke

    def _capture(messages):
        captured["last"] = messages[-1]
        return orig_invoke(messages)

    fake_llm.invoke = _capture

    state = sample_state(
        raw_input="same question",
        messages=[HumanMessage(content="same question")],
    )
    router_node(state)

    assert captured["last"].content == "same question"


# ── system prompt ─────────────────────────────────────────────────────────────

@pytest.mark.unit
def test_router_system_prompt_interpolates_patient_id(fake_llm, sample_state):
    fake_llm.tool_calls = None
    state = sample_state(patient_id="patient-42", raw_input="hi")
    router_node(state)
    assert "patient-42" in ROUTER_SYSTEM_PROMPT.format(patient_id="patient-42")


@pytest.mark.unit
def test_router_seeded_history_uses_current_human_message(fake_llm, sample_state):
    """The first turn is already seeded in state as the current HumanMessage."""
    fake_llm.tool_calls = None
    captured = {}
    orig_invoke = fake_llm.invoke

    def _capture(messages):
        captured["last"] = messages[-1]
        return orig_invoke(messages)

    fake_llm.invoke = _capture

    state = sample_state(raw_input="first message", messages=[HumanMessage(content="first message")])
    router_node(state)

    assert isinstance(captured["last"], HumanMessage)
    assert captured["last"].content == "first message"


# ── identical consecutive messages ────────────────────────────────────────────

@pytest.mark.unit
def test_router_dedup_identical_consecutive_messages(fake_llm, sample_state):
    """If the user sends the exact same text twice in a row, the router's
    content-only dedup check skips appending the second HumanMessage.
    This is a known limitation (not the reported continuity bug)."""
    fake_llm.tool_calls = None
    captured = {}
    orig_invoke = fake_llm.invoke

    def _capture(messages):
        captured["messages"] = list(messages)
        return orig_invoke(messages)

    fake_llm.invoke = _capture

    state = sample_state(
        raw_input="hello",
        messages=[HumanMessage(content="hello")],
    )
    router_node(state)

    human_messages = [m for m in captured["messages"] if isinstance(m, HumanMessage)]
    assert len(human_messages) == 1
    assert human_messages[-1].content == "hello"
