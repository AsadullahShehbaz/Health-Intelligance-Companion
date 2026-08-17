"""Unit tests for app/services/agent_service.py — run_agent + _build_initial_state."""
import pytest

from app.core.llm import validate_llm_connection
from app.schemas.agent import AgentRequest
from app.services.agent_service import _build_initial_state, run_agent


# ── _build_initial_state ─────────────────────────────────────────────────────

@pytest.mark.unit
def test_build_initial_state_defaults():
    req = AgentRequest(patient_id="p1", query="hello")
    state = _build_initial_state(req)
    assert state["patient_id"] == "p1"
    assert state["raw_input"] == "hello"
    assert state["ocr_context"] == ""
    assert state["final_response"] == ""
    assert state["messages"] == []
    assert state["tool_results"] == ""
    assert state["needs_rag"] is False


@pytest.mark.unit
def test_build_initial_state_with_ocr():
    req = AgentRequest(patient_id="p1", query="what is this")
    state = _build_initial_state(req, ocr_text="OCR text here")
    assert state["ocr_context"] == "OCR text here"


# ── run_agent ────────────────────────────────────────────────────────────────

@pytest.mark.unit
async def test_run_agent_returns_response(monkeypatch):
    """With a mocked graph.invoke, run_agent returns an AgentResponse."""
    from app.services import agent_service

    canned_result = {
        "final_response": "You have a cold.",
        "detected_lang": "en",
        "needs_rag": True,
        "retrieval_decision": "correct",
        "retrieved_docs": [{"source": "mayo.com"}, {"source": "who.int"}],
        "saved_memory": True,
    }

    mock_agent = type("MockAgent", (), {"invoke": lambda self, state, config: canned_result})()
    monkeypatch.setattr(agent_service, "agent", mock_agent)

    req = AgentRequest(patient_id="p1", query="I have a fever")
    resp = await run_agent(req)

    assert resp.answer == "You have a cold."
    assert resp.detected_lang == "en"
    assert resp.needs_rag is True
    assert resp.retrieval_decision == "correct"
    assert resp.sources == ["mayo.com", "who.int"]
    assert resp.save_memory is True


@pytest.mark.unit
async def test_run_agent_retries_on_operational_error(monkeypatch):
    """psycopg.OperationalError (Neon wake race) triggers a retry."""
    import psycopg
    from app.services import agent_service

    call_count = {"n": 0}

    class _RetryThen:
        def invoke(self, state, config):
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise psycopg.OperationalError("Neon sleeping")
            return {
                "final_response": "ok",
                "detected_lang": "en",
                "needs_rag": False,
                "retrieved_docs": [],
                "saved_memory": False,
            }

    monkeypatch.setattr(agent_service, "agent", _RetryThen())
    # Patch sleep so the test doesn't actually wait
    async def _noop_sleep(*a, **kw):
        pass
    monkeypatch.setattr("app.services.agent_service.asyncio.sleep", _noop_sleep)

    req = AgentRequest(patient_id="p1", query="hi")
    resp = await run_agent(req)

    assert call_count["n"] == 2  # retried once
    assert resp.answer == "ok"


@pytest.mark.unit
async def test_run_agent_raises_after_max_retries(monkeypatch):
    import psycopg
    from app.services import agent_service

    class _AlwaysFails:
        def invoke(self, state, config):
            raise psycopg.OperationalError("DB down")

    monkeypatch.setattr(agent_service, "agent", _AlwaysFails())
    async def _noop_sleep(*a, **kw):
        pass
    monkeypatch.setattr("app.services.agent_service.asyncio.sleep", _noop_sleep)

    req = AgentRequest(patient_id="p1", query="hi")
    with pytest.raises(psycopg.OperationalError):
        await run_agent(req)


@pytest.mark.unit
async def test_run_agent_non_operational_error_not_retried(monkeypatch):
    from app.services import agent_service

    class _RuntimeFail:
        def invoke(self, state, config):
            raise RuntimeError("graph broke")

    monkeypatch.setattr(agent_service, "agent", _RuntimeFail())

    req = AgentRequest(patient_id="p1", query="hi")
    with pytest.raises(RuntimeError, match="graph broke"):
        await run_agent(req)


@pytest.mark.unit
async def test_run_agent_thread_id_defaults_to_patient_id(monkeypatch):
    """When thread_id is absent, it defaults to patient_id."""
    from app.services import agent_service

    captured_config = {}

    class _CaptureConfig:
        def invoke(self, state, config):
            captured_config.update(config)
            return {
                "final_response": "ok", "detected_lang": "en",
                "needs_rag": False, "retrieved_docs": [], "saved_memory": False,
            }

    monkeypatch.setattr(agent_service, "agent", _CaptureConfig())

    req = AgentRequest(patient_id="patient-99", query="hi")
    await run_agent(req)

    assert captured_config["configurable"]["thread_id"] == "patient-99"


@pytest.mark.unit
async def test_run_agent_uses_thread_id_when_provided(monkeypatch):
    from app.services import agent_service

    captured_config = {}

    class _CaptureConfig:
        def invoke(self, state, config):
            captured_config.update(config)
            return {
                "final_response": "ok", "detected_lang": "en",
                "needs_rag": False, "retrieved_docs": [], "saved_memory": False,
            }

    monkeypatch.setattr(agent_service, "agent", _CaptureConfig())

    req = AgentRequest(
        patient_id="p1", query="hi", thread_id="conv-uuid-123"
    )
    await run_agent(req)

    assert captured_config["configurable"]["thread_id"] == "conv-uuid-123"


# ── thread title generation (first turn only) ───────────────────────────────

def _canned_result():
    return {
        "final_response": "ok", "detected_lang": "en",
        "needs_rag": False, "retrieved_docs": [], "saved_memory": False,
    }


@pytest.mark.unit
async def test_run_agent_titles_new_thread(monkeypatch):
    """First turn (no message history) → LLM title injected into initial state."""
    from types import SimpleNamespace
    from app.services import agent_service

    captured_state = {}

    class _NewThreadAgent:
        def get_state(self, config):
            return SimpleNamespace(values={})  # empty → brand-new thread

        def invoke(self, state, config):
            captured_state.update(state)
            return _canned_result()

    monkeypatch.setattr(agent_service, "agent", _NewThreadAgent())

    async def _fake_title(user_message):
        return "Fever Treatment Advice"

    monkeypatch.setattr(agent_service, "generate_thread_title", _fake_title)

    req = AgentRequest(patient_id="p1", query="I have a fever", thread_id="t-new")
    await run_agent(req)

    assert captured_state["thread_title"] == "Fever Treatment Advice"


@pytest.mark.unit
async def test_run_agent_skips_title_for_existing_thread(monkeypatch):
    """Threads with message history → no title call, no thread_title in state."""
    from types import SimpleNamespace
    from app.services import agent_service

    captured_state = {}

    class _ExistingThreadAgent:
        def get_state(self, config):
            return SimpleNamespace(values={"messages": ["u1", "a1"]})

        def invoke(self, state, config):
            captured_state.update(state)
            return _canned_result()

    monkeypatch.setattr(agent_service, "agent", _ExistingThreadAgent())

    async def _must_not_run(user_message):
        raise AssertionError("generate_thread_title must not run on existing threads")

    monkeypatch.setattr(agent_service, "generate_thread_title", _must_not_run)

    req = AgentRequest(patient_id="p1", query="more fever advice", thread_id="t-old")
    await run_agent(req)

    assert "thread_title" not in captured_state


@pytest.mark.unit
async def test_run_agent_state_check_failure_skips_title(monkeypatch):
    """Fail-open: if the thread-state read errors, the turn still runs —
    just without a generated title."""
    from app.services import agent_service

    captured_state = {}

    class _BrokenGetStateAgent:
        def get_state(self, config):
            raise RuntimeError("checkpointer unreachable")

        def invoke(self, state, config):
            captured_state.update(state)
            return _canned_result()

    monkeypatch.setattr(agent_service, "agent", _BrokenGetStateAgent())

    async def _must_not_run(user_message):
        raise AssertionError("title generation must be skipped when state check fails")

    monkeypatch.setattr(agent_service, "generate_thread_title", _must_not_run)

    req = AgentRequest(patient_id="p1", query="hello", thread_id="t-x")
    resp = await run_agent(req)

    assert resp.answer == "ok"
    assert "thread_title" not in captured_state


@pytest.mark.unit
def test_validate_llm_connection_reports_unreachable_backend(monkeypatch):
    import httpx

    def _raise_connect_error(*args, **kwargs):
        raise httpx.ConnectError("connection refused")

    monkeypatch.setattr("app.core.llm.httpx.get", _raise_connect_error)

    with pytest.raises(RuntimeError, match="LLM backend|LLM_BASE_URL|llama-server"):
        validate_llm_connection()
