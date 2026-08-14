"""Unit tests for app/services/agent_service.py — run_agent + _build_initial_state."""
import pytest

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
