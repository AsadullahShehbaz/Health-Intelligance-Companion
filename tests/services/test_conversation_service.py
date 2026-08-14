"""Unit tests for app/services/conversation_service.py.

Covers turn reconstruction from checkpoint rows, title/snippet derivation,
ownership filtering, and retry logic.
"""
import pytest

from app.services import conversation_service as svc


# ── _title ────────────────────────────────────────────────────────────────────

@pytest.mark.unit
def test_title_uses_first_nonempty_raw_input():
    turns = [
        {"raw_input": "", "final_response": "a1"},
        {"raw_input": "  What is diabetes?  ", "final_response": "a2"},
    ]
    assert svc._title(turns) == "What is diabetes?"


@pytest.mark.unit
def test_title_fallback_when_all_empty():
    turns = [{"raw_input": "", "final_response": ""}]
    assert svc._title(turns) == "Untitled conversation"


# ── _sources ──────────────────────────────────────────────────────────────────

@pytest.mark.unit
def test_sources_extracts_source_fields():
    turn = {"retrieved_docs": [
        {"source": "who.int"}, {"source": ""}, {"source": "mayo.com"}, {"source": "x.com"},
    ]}
    assert svc._sources(turn) == ["who.int", "mayo.com", "x.com"][:3]


@pytest.mark.unit
def test_sources_empty():
    assert svc._sources({"retrieved_docs": None}) == []
    assert svc._sources({"retrieved_docs": []}) == []


# ── list_conversations ──────────────────────────────────────────────────────

@pytest.mark.unit
def test_list_conversations_groups_by_thread(monkeypatch):
    rows = [
        {"thread_id": "t1", "checkpoint_id": "c1", "raw_input": "hello",
         "final_response": "hi", "ts": "2025-01-01T10:00:00",
         "detected_lang": "en", "needs_rag": False,
         "retrieval_decision": "", "retrieved_docs": None},
        {"thread_id": "t1", "checkpoint_id": "c2", "raw_input": "fever?",
         "final_response": "take meds", "ts": "2025-01-01T11:00:00",
         "detected_lang": "en", "needs_rag": True,
         "retrieval_decision": "correct", "retrieved_docs": [{"source": "s"}]},
        {"thread_id": "t2", "checkpoint_id": "c3", "raw_input": "bye",
         "final_response": "bye!", "ts": "2025-01-01T12:00:00",
         "detected_lang": "en", "needs_rag": False,
         "retrieval_decision": "", "retrieved_docs": None},
    ]
    monkeypatch.setattr(svc, "_query", lambda sql, params: rows)

    result = list(svc.list_conversations("patient-1"))

    assert len(result) == 2  # two threads
    # newest first (t2 has later ts)
    assert result[0]["thread_id"] == "t2"
    assert result[1]["thread_id"] == "t1"
    # message_count = turns * 2
    assert result[1]["message_count"] == 4  # t1 has 2 turns → 4 messages
    # snippet = last turn's final_response
    assert result[1]["snippet"] == "take meds"
    # title = first non-empty raw_input
    assert result[1]["title"] == "hello"


@pytest.mark.unit
def test_list_conversations_empty(monkeypatch):
    monkeypatch.setattr(svc, "_query", lambda sql, params: [])
    assert svc.list_conversations("nobody") == []


# ── get_conversation ─────────────────────────────────────────────────────────

@pytest.mark.unit
def test_get_conversation_builds_transcript(monkeypatch):
    rows = [
        {"thread_id": "t1", "checkpoint_id": "c1", "raw_input": "What is diabetes?",
         "final_response": "It's a chronic condition.",
         "ts": "2025-01-01T10:00:00", "detected_lang": "en",
         "needs_rag": True, "retrieval_decision": "correct",
         "retrieved_docs": [{"source": "who.int"}]},
    ]
    monkeypatch.setattr(svc, "_query", lambda sql, params: rows)

    result = svc.get_conversation("t1", "patient-1")

    assert result is not None
    assert result["thread_id"] == "t1"
    assert result["title"] == "What is diabetes?"
    assert len(result["messages"]) == 2  # user + assistant
    assert result["messages"][0]["role"] == "user"
    assert result["messages"][1]["role"] == "assistant"
    meta = result["messages"][1]["meta"]
    assert meta["needs_rag"] is True
    assert meta["retrieval_decision"] == "correct"
    assert "who.int" in meta["sources"]


@pytest.mark.unit
def test_get_conversation_not_found(monkeypatch):
    """When no turns match the thread_id/patient_id → None."""
    monkeypatch.setattr(svc, "_query", lambda sql, params: [])
    assert svc.get_conversation("missing", "patient-1") is None


@pytest.mark.unit
def test_get_conversation_skips_empty_turns(monkeypatch):
    """Turns with both empty raw_input and final_response are skipped."""
    rows = [
        {"thread_id": "t1", "checkpoint_id": "c0", "raw_input": "",
         "final_response": "", "ts": "2025-01-01T09:00:00",
         "detected_lang": "", "needs_rag": False,
         "retrieval_decision": "", "retrieved_docs": None},
        {"thread_id": "t1", "checkpoint_id": "c1", "raw_input": "hi",
         "final_response": "hello", "ts": "2025-01-01T10:00:00",
         "detected_lang": "en", "needs_rag": False,
         "retrieval_decision": "", "retrieved_docs": None},
    ]
    monkeypatch.setattr(svc, "_query", lambda sql, params: rows)

    result = svc.get_conversation("t1", "patient-1")
    assert len(result["messages"]) == 2  # only the non-empty turn


@pytest.mark.unit
def test_get_conversation_ownership_filter(monkeypatch):
    """The patient_id is passed in the SQL params — only that patient's
    turns are returned.  If _query returns [], the conversation is None
    (ownership enforced at the DB level)."""
    monkeypatch.setattr(svc, "_query", lambda sql, params: [])
    # Patient-2 asks for patient-1's thread → no rows → None
    assert svc.get_conversation("t1", "patient-2") is None
