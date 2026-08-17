"""Unit tests for app/services/voice_service.py — transcribe_audio."""
import pytest

from app.services.voice_service import (
    MAX_FILE_SIZE,
    STT_MODEL,
    GROQ_STT_URL,
    transcribe_audio,
)


def _mock_httpx_client(monkeypatch, response_json, status_code=200, raise_exc=None):
    """Patch httpx.AsyncClient to return a canned response."""
    from unittest.mock import AsyncMock

    mock_response = AsyncMock()
    mock_response.status_code = status_code
    mock_response.raise_for_status = AsyncMock()
    if raise_exc:
        mock_response.raise_for_error = AsyncMock(side_effect=raise_exc)
    mock_response.json = AsyncMock(return_value=response_json)

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    monkeypatch.setattr("httpx.AsyncClient", lambda: mock_client)
    return mock_client


@pytest.mark.unit
async def test_empty_audio_returns_empty_string():
    result = await transcribe_audio(b"", "audio/webm")
    assert result == ""


@pytest.mark.unit
async def test_file_too_large_raises(monkeypatch):
    from fastapi import HTTPException

    big_blob = b"x" * (MAX_FILE_SIZE + 1)
    with pytest.raises(HTTPException) as exc_info:
        await transcribe_audio(big_blob, "audio/webm")
    assert exc_info.value.status_code == 413


@pytest.mark.unit
async def test_successful_transcription(monkeypatch):
    _mock_httpx_client(
        monkeypatch,
        response_json={"text": "I have a headache"},
        status_code=200,
    )
    result = await transcribe_audio(b"fake-audio-bytes", "audio/webm")
    assert result == "I have a headache"


@pytest.mark.unit
async def test_transcription_whitespace_only(monkeypatch):
    _mock_httpx_client(
        monkeypatch,
        response_json={"text": "   "},
        status_code=200,
    )
    result = await transcribe_audio(b"fake-audio-bytes", "audio/webm")
    assert result == ""


@pytest.mark.unit
async def test_groq_http_error_propagates(monkeypatch):
    import httpx

    _mock_httpx_client(
        monkeypatch,
        response_json={"error": "bad request"},
        status_code=400,
        raise_exc=httpx.HTTPStatusError(
            "Bad Request",
            request=None,
            response=None,
        ),
    )
    with pytest.raises(Exception):
        await transcribe_audio(b"fake-audio-bytes", "audio/webm")


@pytest.mark.unit
async def test_groq_network_failure_propagates(monkeypatch):
    _mock_httpx_client(
        monkeypatch,
        response_json=None,
        status_code=500,
        raise_exc=RuntimeError("connection lost"),
    )
    with pytest.raises(Exception):
        await transcribe_audio(b"fake-audio-bytes", "audio/webm")
