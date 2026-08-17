# app/api/voice.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from app.deps import get_current_user
from app.models.user import User
from app.services.voice_service import process_voice_turn
from app.schemas.agent import AgentRequest
from app.core.voice import tts_streaming_playback

router = APIRouter(prefix="/voice", tags=["Voice"])

@router.post("/interact")
async def voice_interaction(
    thread_id: str = None, 
    user: User = Depends(get_current_user)
):
    """
    Triggers local microphone capture, feeds transcript to the multi-node agent,
    plays back response audio, and returns full interaction payload.
    """
    try:
        result = await process_voice_turn(
            patient_id=str(user.id), 
            thread_id=thread_id
        )
        return {
            "transcript": result["user_transcript"],
            "response": result["agent_response"],
            "thread_id": result["thread_id"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice processing failed: {str(e)}")

@router.post("/tts")
async def text_to_speech_playback(text: str):
    """
    Synthesizes and plays back arbitrary text strings using Edge TTS engine.
    """
    audio_bytes = await tts_streaming_playback(text)
    return Response(content=audio_bytes, media_type="audio/mpeg")