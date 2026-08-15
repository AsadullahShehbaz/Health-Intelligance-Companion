"""Unit tests for app/agent/tools.py — RAG and web-search tools."""
import pytest

from app.agent.tools import TOOLS


# ── TOOLS list ───────────────────────────────────────────────────────────────

@pytest.mark.unit
def test_tools_list_has_expected_tools():
    names = {t.name for t in TOOLS}
    assert names == {
        "retrieve_medical_knowledge",
        "search_web_medical",
    }


# ── retrieve_medical_knowledge ──────────────────────────────────────────────

@pytest.mark.unit
def test_retrieve_medical_knowledge_success(monkeypatch, fake_qdrant):
    """With mocked Qdrant returning high-score docs → formatted result."""
    from app.agent.tools import retrieve_medical_knowledge
    result = retrieve_medical_knowledge.invoke({"query": "diabetes"})
    assert "Retrieval decision" in result
    assert "who.int" in result  # from fake_qdrant canned docs


@pytest.mark.unit
def test_retrieve_medical_knowledge_no_docs(monkeypatch):
    """When retrieve returns empty → 'No relevant documents found.'"""
    from app.agent.tools import retrieve_medical_knowledge
    monkeypatch.setattr("app.agent.tools.corrective_retrieve", lambda *a, **k: {
        "docs": [], "decision": "incorrect", "avg_score": 0.0,
    })
    result = retrieve_medical_knowledge.invoke({"query": "obscure"})
    assert "No relevant documents" in result


@pytest.mark.unit
def test_retrieve_medical_knowledge_handles_error(monkeypatch):
    """If corrective_retrieve raises → error string, not exception."""
    from app.agent.tools import retrieve_medical_knowledge
    monkeypatch.setattr(
        "app.agent.tools.corrective_retrieve",
        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    result = retrieve_medical_knowledge.invoke({"query": "x"})
    assert "Error" in result
