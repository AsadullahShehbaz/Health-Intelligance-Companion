"""Unit tests for app/services/chat_service.py — stream_chat queue bridge."""
import pytest

from app.services.chat_service import stream_chat


@pytest.mark.unit
async def test_stream_chat_yields_chunks(fake_llm):
    """Chunks from the LLM's astream are yielded as plain strings."""
    fake_llm.stream_chunks = ["Hello", " ", "world"]
    messages = [{"role": "user", "content": "hi"}]

    tokens = [t async for t in stream_chat(messages, temperature=0.7, max_tokens=100)]

    assert "".join(tokens) == "Hello world"


@pytest.mark.unit
async def test_stream_chat_skips_empty_chunks(fake_llm):
    fake_llm.stream_chunks = ["a", "", "b"]
    messages = [{"role": "user", "content": "hi"}]
    tokens = [t async for t in stream_chat(messages, temperature=0.5, max_tokens=10)]
    assert tokens == ["a", "b"]


@pytest.mark.unit
async def test_stream_chat_error_sentinel(fake_llm):
    """When the LLM raises, stream_chat yields the error sentinel."""
    fake_llm.should_error = True
    messages = [{"role": "user", "content": "hi"}]

    tokens = [t async for t in stream_chat(messages, temperature=0.7, max_tokens=100)]

    assert tokens == ["\n\nServer Error"]


@pytest.mark.unit
async def test_stream_chat_converts_role_map(fake_llm, monkeypatch):
    """Messages dict is converted to LangChain message objects before calling
    the LLM.  Verify by capturing the messages list."""
    captured = []

    async def _fake_astream(messages, **kwargs):
        captured.extend(type(m).__name__ for m in messages)
        from types import SimpleNamespace
        yield SimpleNamespace(content="ok")

    fake_llm.astream = _fake_astream
    messages = [
        {"role": "system", "content": "be helpful"},
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "hi"},
    ]
    list_async_gen = [t async for t in stream_chat(messages, temperature=0.5, max_tokens=10)]
    assert "SystemMessage" in captured
    assert "HumanMessage" in captured
    assert "AIMessage" in captured
