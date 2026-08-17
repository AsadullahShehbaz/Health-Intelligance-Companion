# app/services/voice_service.py
import asyncio
import os
import time
import httpx
from fastapi import HTTPException

from app.config import settings
from app.utils.logging_config import get_logger
from app.core.voice import capture_and_transcribe, tts_streaming_playback
from app.services.agent_service import run_agent
from app.schemas.agent import AgentRequest

logger = get_logger(__name__)

GROQ_STT_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB
MAX_DURATION_SECONDS = 60
STT_MODEL = "whisper-large-v3-turbo"


async def transcribe_audio(file_bytes: bytes, content_type: str) -> str:
    """Transcribe audio bytes using Groq's Whisper endpoint."""
    if not file_bytes:
        return ""

    if len(file_bytes) > MAX_FILE_SIZE:
        logger.warning("STT file too large: %d bytes", len(file_bytes))
        raise HTTPException(status_code=413, detail="Audio file too large")

    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
    }

    files = {
        "file": ("audio.webm", file_bytes, content_type or "audio/webm"),
        "model": (None, STT_MODEL),
        "language": (None, "en"),
        "response_format": (None, "json"),
    }

    try:
        start = time.monotonic()
        async with httpx.AsyncClient() as client:
            response = await client.post(
                GROQ_STT_URL,
                headers=headers,
                files=files,
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            text = (data.get("text") or "").strip()
            logger.info(
                "✓ STT completed in %.2fs | chars=%d",
                time.monotonic() - start,
                len(text),
            )
            return text
    except httpx.HTTPStatusError as exc:
        logger.error("Groq STT failed: %s", exc.response.text)
        raise HTTPException(
            status_code=exc.response.status_code,
            detail="Speech recognition service error",
        )
    except Exception:
        logger.exception("STT request failed")
        raise HTTPException(status_code=500, detail="Speech recognition failed")


async def process_voice_turn(
    patient_id: str, thread_id: str = None
) -> dict:
    """
    Full voice interaction loop:
      1. Capture mic audio → transcribe (local Whisper / Google STT)
      2. Feed transcript into the multi-node health agent
      3. Speak the agent response back via Edge TTS
      4. Return transcript, response text, and thread_id
    """
    # --- 1. Capture & transcribe (synchronous, run in thread) ---
    try:
        transcript = await asyncio.to_thread(capture_and_transcribe)
    except Exception:
        logger.exception("Microphone capture / transcription failed")
        raise HTTPException(
            status_code=500, detail="Microphone capture or transcription failed"
        )

    if not transcript:
        return {"user_transcript": "", "agent_response": "", "thread_id": thread_id or patient_id}

    # --- 2. Run agent ---
    req = AgentRequest(patient_id=patient_id, query=transcript, thread_id=thread_id)
    agent_response = await run_agent(req)

    # --- 3. TTS playback ---
    try:
        await tts_streaming_playback(agent_response.answer)
    except Exception:
        logger.warning("TTS playback failed (non-fatal)", exc_info=True)

    return {
        "user_transcript": transcript,
        "agent_response": agent_response.answer,
        "thread_id": thread_id or patient_id,
    }
