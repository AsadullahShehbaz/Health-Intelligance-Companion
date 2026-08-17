# app/services/voice_service.py
import asyncio
from app.core.voice import capture_and_transcribe, tts_streaming_playback
from app.services.agent_service import run_agent
from app.schemas.agent import AgentRequest, AgentResponse
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

async def process_voice_turn(patient_id: str, thread_id: str = None) -> dict:
    """
    Executes a complete Voice-to-Voice pipeline turn:
    1. Capture Speech -> STT
    2. Invoke LangGraph Agent Engine
    3. Generate Audio Response via TTS -> Playback
    """
    # 1. Speech to Text (run in threadpool to prevent blocking async event loop)
    user_transcript = await asyncio.to_thread(capture_and_transcribe)
    
    # 2. Invoke Existing Health Agent Pipeline
    request = AgentRequest(
        patient_id=patient_id,
        query=user_transcript,
        thread_id=thread_id
    )
    agent_response: AgentResponse = await run_agent(request, ocr_text="")
    
    # 3. Text to Speech & Playback
    audio_bytes = await tts_streaming_playback(agent_response.answer)
    
    return {
        "user_transcript": user_transcript,
        "agent_response": agent_response.answer,
        "thread_id": thread_id,
        "audio_bytes": audio_bytes
    }