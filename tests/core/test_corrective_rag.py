"""Unit tests for app/core/rag/corrective_rag.py.

Covers:
- evaluate_relevance thresholds (correct / ambiguous / incorrect)
- web_search_fallback with mocked SerpAPI
- corrective_retrieve pipeline (retrieve → evaluate → correct)
"""
import pytest

from app.core.rag.corrective_rag import (
    AMBIGUOUS_THRESHOLD,
    RELEVANCE_THRESHOLD,
    corrective_retrieve,
    evaluate_relevance,
    web_search_fallback,
)


# ── evaluate_relevance ───────────────────────────────────────────────────────

@pytest.mark.unit
def test_evaluate_relevance_empty_docs():
    decision, avg = evaluate_relevance([])
    assert decision == "incorrect"
    assert avg == 0.0


@pytest.mark.unit
def test_evaluate_relevance_correct():
    """max_score >= RELEVANCE_THRESHOLD → correct"""
    docs = [
        {"score": 0.6},
        {"score": 0.4},
    ]
    decision, avg = evaluate_relevance(docs)
    assert decision == "correct"
    assert avg == 0.5


@pytest.mark.unit
def test_evaluate_relevance_ambiguous():
    """max < RELEVANCE_THRESHOLD but avg >= AMBIGUOUS_THRESHOLD → ambiguous"""
    docs = [
        {"score": 0.4},
        {"score": 0.36},
    ]
    decision, avg = evaluate_relevance(docs)
    assert decision == "ambiguous"
    assert abs(avg - 0.38) < 0.001


@pytest.mark.unit
def test_evaluate_relevance_incorrect():
    """max < RELEVANCE_THRESHOLD and avg < AMBIGUOUS_THRESHOLD → incorrect"""
    docs = [
        {"score": 0.2},
        {"score": 0.1},
    ]
    decision, avg = evaluate_relevance(docs)
    assert decision == "incorrect"
    assert avg == pytest.approx(0.15)


@pytest.mark.unit
def test_evaluate_relevance_single_doc_correct():
    docs = [{"score": 0.9}]
    decision, _ = evaluate_relevance(docs)
    assert decision == "correct"


@pytest.mark.unit
def test_thresholds_are_sane():
    """RELEVANCE must be strictly greater than AMBIGUOUS."""
    assert RELEVANCE_THRESHOLD > AMBIGUOUS_THRESHOLD
    assert RELEVANCE_THRESHOLD == 0.5
    assert AMBIGUOUS_THRESHOLD == 0.35


# ── web_search_fallback ──────────────────────────────────────────────────────

@pytest.mark.unit
def test_web_search_fallback_returns_docs(fake_serpapi):
    docs = web_search_fallback("diabetes symptoms")
    assert len(docs) >= 1
    assert all("text" in d and "source" in d for d in docs)
    assert all(d["category"] == "web" for d in docs)
    assert all(d["score"] == 0.5 for d in docs)


@pytest.mark.unit
def test_web_search_fallback_handles_error(monkeypatch):
    """If GoogleSearch raises, fallback returns [] (caught, not propagated)."""
    class _Boom:
        def __init__(self, params):
            raise RuntimeError("SerpAPI down")

    monkeypatch.setattr("app.core.rag.corrective_rag.GoogleSearch", _Boom)
    assert web_search_fallback("anything") == []


# ── corrective_retrieve ──────────────────────────────────────────────────────

@pytest.mark.unit
def test_corrective_retrieve_correct(fake_qdrant):
    """High-score docs → 'correct', no web search."""
    result = corrective_retrieve("What is diabetes?")
    assert result["decision"] == "correct"
    assert len(result["docs"]) <= 5
    assert result["avg_score"] > 0


@pytest.mark.unit
def test_corrective_retrieve_incorrect_triggers_web_search(monkeypatch, fake_serpapi):
    """Low-score docs → 'incorrect', web search prepended."""
    low_docs = [{"text": "irrelevant", "source": "x", "category": "y", "score": 0.1}]
    monkeypatch.setattr("app.core.rag.corrective_rag.retrieve", lambda *a, **k: low_docs)
    result = corrective_retrieve("obscure query")
    assert result["decision"] == "incorrect"
    # Web results (category="web") should be prepended
    web_docs = [d for d in result["docs"] if d.get("category") == "web"]
    assert len(web_docs) >= 1


@pytest.mark.unit
def test_corrective_retrieve_ambiguous_appends_web_search(monkeypatch, fake_serpapi):
    """Ambiguous scores → web search appended after Qdrant docs."""
    mid_docs = [{"text": "partial", "source": "q", "category": "c", "score": 0.36}]
    monkeypatch.setattr("app.core.rag.corrective_rag.retrieve", lambda *a, **k: mid_docs)
    result = corrective_retrieve("partial query")
    assert result["decision"] == "ambiguous"
    # Web results should be present
    web_docs = [d for d in result["docs"] if d.get("category") == "web"]
    assert len(web_docs) >= 1


@pytest.mark.unit
def test_corrective_retrieve_caps_at_five_docs(fake_qdrant, fake_serpapi):
    result = corrective_retrieve("query")
    assert len(result["docs"]) <= 5


@pytest.mark.unit
def test_corrective_retrieve_returns_avg_score(fake_qdrant):
    result = corrective_retrieve("diabetes")
    assert "avg_score" in result
    assert isinstance(result["avg_score"], float)
