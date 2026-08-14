"""Unit tests for app/agent/graph.py — routing and tool execution."""
import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from app.agent.graph import _extract_tool_metadata, _route_after_router, _run_tools


# ── _route_after_router ──────────────────────────────────────────────────────

@pytest.mark.unit
def test_route_to_tools_when_tool_calls_present():
    """When the last message is an AIMessage with tool_calls → route to 'tools'."""
    state = {
        "messages": [
            HumanMessage(content="hello"),
            AIMessage(
                content="",
                tool_calls=[{"name": "fetch_patient_facts", "args": {}, "id": "1"}],
            ),
        ]
    }
    assert _route_after_router(state) == "tools"


@pytest.mark.unit
def test_route_to_biomistral_when_no_tool_calls(sample_state):
    """When the last message is a plain AIMessage (no tool_calls) → biomistral."""
    state = sample_state(messages=[
        HumanMessage(content="hello"),
        AIMessage(content="hi there"),
    ])
    assert _route_after_router(state) == "biomistral"


@pytest.mark.unit
def test_route_to_biomistral_when_last_is_human():
    """No-tool turn: the router stored only the user message, so the last
    message is a HumanMessage → straight to BioMistral."""
    state = {"messages": [HumanMessage(content="hello")]}
    assert _route_after_router(state) == "biomistral"


@pytest.mark.unit
def test_route_to_biomistral_on_empty_history():
    """Edge case: no messages at all → BioMistral (no tools to run)."""
    assert _route_after_router({"messages": []}) == "biomistral"


# ── _extract_tool_metadata ────────────────────────────────────────────────────

@pytest.mark.unit
def test_extract_metadata_from_rag_tool_message():
    """needs_rag / retrieval_decision / sources are parsed from a
    retrieve_medical_knowledge ToolMessage."""
    tool_msg = ToolMessage(
        content=(
            "[Retrieval decision: correct]\n\n"
            "[who.int] Diabetes is a chronic condition.\n"
            "[mayoclinic.org] Symptoms include thirst.\n"
        ),
        tool_call_id="tc1",
        name="retrieve_medical_knowledge",
    )
    meta = _extract_tool_metadata([tool_msg])

    assert meta["needs_rag"] is True
    assert meta["retrieval_decision"] == "correct"
    assert meta["retrieved_docs"][0]["source"] == "who.int"
    assert "Diabetes is a chronic condition" in meta["tool_results"]
    assert meta["saved_memory"] is False


@pytest.mark.unit
def test_extract_metadata_detects_saved_memory():
    meta = _extract_tool_metadata([
        ToolMessage(
            content="Saved to patient record: fever (ongoing)",
            tool_call_id="tc1",
            name="save_patient_fact",
        )
    ])
    assert meta["saved_memory"] is True
    assert meta["needs_rag"] is False


@pytest.mark.unit
def test_extract_metadata_empty():
    meta = _extract_tool_metadata([])
    assert meta["tool_results"] == ""
    assert meta["needs_rag"] is False
    assert meta["saved_memory"] is False
    assert meta["retrieval_decision"] == ""
    assert meta["retrieved_docs"] == []


# ── _run_tools ───────────────────────────────────────────────────────────────

@pytest.mark.unit
def test_run_tools_executes_and_extracts(monkeypatch, fake_store):
    """_run_tools invokes the ToolNode, appends ToolMessages, and folds the
    results into tool_results + metadata."""
    from app.agent import graph as graph_mod
    from app.agent import tools as tools_mod
    monkeypatch.setattr(tools_mod, "store", fake_store)

    def _fake_tool_node_invoke(state):
        tool_msg = ToolMessage(
            content="[Retrieval decision: correct]\n\n[who.int] Diabetes info",
            tool_call_id="call_1",
            name="retrieve_medical_knowledge",
        )
        state["messages"] = state["messages"] + [tool_msg]
        return state

    monkeypatch.setattr(graph_mod._tool_node, "invoke", _fake_tool_node_invoke)

    ai_msg = AIMessage(
        content="",
        tool_calls=[{
            "name": "retrieve_medical_knowledge",
            "args": {"query": "diabetes"},
            "id": "call_1",
        }],
    )
    state = {
        "messages": [HumanMessage(content="what is diabetes?"), ai_msg],
        "patient_id": "p1",
    }
    result = _run_tools(state)

    # ToolMessage appended
    assert any(isinstance(m, ToolMessage) for m in result["messages"])
    # Metadata folded in
    assert result["needs_rag"] is True
    assert result["retrieval_decision"] == "correct"
    assert "Diabetes info" in result["tool_results"]
