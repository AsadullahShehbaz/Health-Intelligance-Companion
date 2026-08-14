"""Unit tests for app/services/rag_chat_service.py — _build_prompt + stream_rag_chat."""
import pytest

from app.services.rag_chat_service import _build_prompt, stream_rag_chat


# ── _build_prompt ─────────────────────────────────────────────────────────────

@pytest.mark.unit
def test_build_prompt_includes_query():
    prompt = _build_prompt("What is diabetes?", [{"text": "x", "source": "src"}])
    assert "What is diabetes?" in prompt
    assert "Answer:" in prompt


@pytest.mark.unit
def test_build_prompt_includes_doc_text():
    docs = [{"text": "Diabetes is chronic.", "source": "who.int"}]
    prompt = _build_prompt("q", docs)
    assert "Diabetes is chronic." in prompt
    assert "who.int" in prompt


@pytest.mark.unit
def test_build_prompt_truncates_to_300_chars():
    long_text = "A" * 500
    docs = [{"text": long_text, "source": "src"}]
    prompt = _build_prompt("q", docs)
    # The text should be truncated to 300 chars in the prompt
    assert "A" * 300 in prompt
    assert "A" * 301 not in prompt


@pytest.mark.unit
def test_build_prompt_uses_top_3_docs():
    docs = [
        {"text": f"doc{i}", "source": f"src{i}"} for i in range(5)
    ]
    prompt = _build_prompt("q", docs)
    assert "doc0" in prompt
    assert "doc1" in prompt
    assert "doc2" in prompt
    assert "doc3" not in prompt  # only top 3


@pytest.mark.unit
def test_build_prompt_empty_docs():
    prompt = _build_prompt("hello", [])
    assert "hello" in prompt
    assert "Answer:" in prompt


# ── stream_rag_chat ──────────────────────────────────────────────────────────

@pytest.mark.unit
async def test_stream_rag_chat_yields_chunks(fake_llm, fake_qdrant):
    fake_llm.stream_chunks = ["RAG", " ", "answer"]
    messages = [{"role": "user", "content": "What is diabetes?"}]

    tokens = [t async for t in stream_rag_chat(messages, temperature=0.5, max_tokens=100)]
    assert "".join(tokens) == "RAG answer"


@pytest.mark.unit
async def test_stream_rag_chat_error_sentinel(fake_llm, fake_qdrant):
    fake_llm.should_error = True
    messages = [{"role": "user", "content": "hi"}]

    tokens = [t async for t in stream_rag_chat(messages, temperature=0.5, max_tokens=100)]
    assert tokens == ["\n\nServer Error"]


@pytest.mark.unit
async def test_stream_rag_chat_uses_last_message_as_query(fake_llm, fake_qdrant, monkeypatch):
    """The last user message's content is what gets sent to corrective_retrieve."""
    captured_query = []

    original_retrieve = fake_qdrant

    def _spy_retrieve(query, top_k=5, category=None):
        captured_query.append(query)
        return original_retrieve(query, top_k=top_k, category=category)

    monkeypatch.setattr("app.core.rag.corrective_rag.retrieve", _spy_retrieve)

    messages = [
        {"role": "user", "content": "earlier question"},
        {"role": "assistant", "content": "earlier answer"},
        {"role": "user", "content": "What is diabetes?"},
    ]
    _ = [t async for t in stream_rag_chat(messages, temperature=0.5, max_tokens=50)]
    assert captured_query[-1] == "What is diabetes?"
