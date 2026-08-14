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
    """When the router decides no tools are needed, only the user's
    HumanMessage is persisted — no intermediate assistant text."""
    fake_llm.response_text = "irrelevant"
    fake_llm.tool_calls = None

    state = sample_state(raw_input="Hello there")
    result = router_node(state)

    assert len(result["messages"]) == 1
    assert isinstance(result["messages"][0], HumanMessage)
    assert result["messages"][0].content == "Hello there"
    # No answer / final_response set by the router
    assert "answer" not in result
    assert "final_response" not in result


# ── tool-call path ────────────────────────────────────────────────────────────

@pytest.mark.unit
def test_router_tool_call_stores_user_and_ai(fake_llm, sample_state):
    """When the router emits tool_calls, both the user message and the
    AIMessage(tool_calls) are stored so the ToolNode can execute them."""
    fake_llm.tool_calls = [{"name": "save_patient_fact", "args": {}, "id": "tc1"}]

    state = sample_state(raw_input="I have a fever")
    result = router_node(state)

    assert len(result["messages"]) == 2
    assert isinstance(result["messages"][0], HumanMessage)
    assert result["messages"][0].content == "I have a fever"
    assert isinstance(result["messages"][1], AIMessage)
    assert result["messages"][1].tool_calls  # truthy


# ── current input appended to the LLM call ───────────────────────────────────

@pytest.mark.unit
def test_router_appends_input_when_history_ends_on_ai(fake_llm, sample_state):
    """At the start of a turn the history ends on an assistant message, so
    the router appends the current input to the messages it sends to the LLM.
    The fake LLM records the last message it was invoked with."""
    fake_llm.tool_calls = None
    captured = {}
    orig_invoke = fake_llm.invoke

    def _capture(messages):
        captured["last"] = messages[-1]
        return orig_invoke(messages)

    fake_llm.invoke = _capture

    state = sample_state(
        raw_input="new question",
        messages=[HumanMessage(content="old q"), AIMessage(content="old a")],
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
def test_router_empty_history_appends_input(fake_llm, sample_state):
    """First turn ever — history is empty, router still sends the input."""
    fake_llm.tool_calls = None
    captured = {}
    orig_invoke = fake_llm.invoke

    def _capture(messages):
        captured["last"] = messages[-1]
        return orig_invoke(messages)

    fake_llm.invoke = _capture

    state = sample_state(raw_input="first message", messages=[])
    router_node(state)

    assert isinstance(captured["last"], HumanMessage)
    assert captured["last"].content == "first message"
