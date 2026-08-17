"""Unit tests for app/services/title_service.py — generate_thread_title."""
import pytest
from langchain_core.messages import AIMessage

from app.services.title_service import DEFAULT_TITLE, generate_thread_title


def _llm_returning(content, exc=None):
    """Stand-in for the title_llm ChatGroq instance: patch .ainvoke's result."""
    from unittest.mock import AsyncMock

    mock = AsyncMock()
    if exc is not None:
        mock.ainvoke.side_effect = exc
    else:
        mock.ainvoke.return_value = AIMessage(content=content)
    return mock


@pytest.mark.unit
async def test_short_message_skips_llm():
    """Tiny/empty messages default without an LLM call."""
    import app.services.title_service as svc

    with pytest.MonkeyPatch.context() as mp:
        mock_llm = _llm_returning("Should Not Be Called")
        mp.setattr(svc, "title_llm", mock_llm)
        assert await generate_thread_title("") == DEFAULT_TITLE
        assert await generate_thread_title("  ") == DEFAULT_TITLE
        assert await generate_thread_title("hi") == DEFAULT_TITLE
        mock_llm.ainvoke.assert_not_awaited()


@pytest.mark.unit
async def test_returns_clean_title():
    import app.services.title_service as svc

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(svc, "title_llm", _llm_returning("Vitamin D Deficiency Symptoms"))
        title = await generate_thread_title(
            "I feel tired all the time, could it be vitamin D?"
        )
        assert title == "Vitamin D Deficiency Symptoms"


@pytest.mark.unit
async def test_strips_quotes_and_title_prefix():
    import app.services.title_service as svc

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(
            svc, "title_llm",
            _llm_returning('"Title: Persistent Headache Advice"'),
        )
        title = await generate_thread_title("my head hurts since monday")
        assert title == "Persistent Headache Advice"


@pytest.mark.unit
async def test_collapses_multiline_whitespace():
    """Multi-line LLM output becomes a single-line sidebar title."""
    import app.services.title_service as svc

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(
            svc, "title_llm",
            _llm_returning("Lab Report\n  Review   Results"),
        )
        title = await generate_thread_title("please review my lab report")
        assert title == "Lab Report Review Results"


@pytest.mark.unit
async def test_truncates_long_title_at_word_boundary():
    import app.services.title_service as svc

    long_content = " ".join(["word"] * 40)  # 200 chars
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(svc, "title_llm", _llm_returning(long_content))
        title = await generate_thread_title("long query here")
        assert len(title) <= 80
        assert not title.endswith(" ")   # cut at a word boundary
        assert title == " ".join(title.split())


@pytest.mark.unit
async def test_llm_failure_defaults():
    import app.services.title_service as svc

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(svc, "title_llm", _llm_returning(None, exc=RuntimeError("boom")))
        assert await generate_thread_title("I have a fever") == DEFAULT_TITLE


@pytest.mark.unit
async def test_blank_llm_response_defaults():
    import app.services.title_service as svc

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(svc, "title_llm", _llm_returning("   "))
        assert await generate_thread_title("I have a fever") == DEFAULT_TITLE
