# app/core/voice.py
import io
import asyncio
import edge_tts
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

_playback_lock = asyncio.Lock()
_is_playing = False


def stop_audio():
    """No server-side playback in the cloud; kept for API compatibility."""
    global _is_playing
    _is_playing = False
    logger.info("Playback stopped by request.")


def capture_and_transcribe(pause_threshold: float = 2.0) -> str:
    """Local-microphone capture. Only works on a desktop machine."""
    import speech_recognition as sr  # lazy import: needs PyAudio
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        recognizer.pause_threshold = pause_threshold
        audio = recognizer.listen(source)
        return recognizer.recognize_google(audio)


async def tts_streaming_playback(speech: str, voice: str = "en-US-GuyNeural") -> bytes:
    """
    Converts text to speech using Edge TTS, plays audio directly to local speakers,
    and returns raw MP3 bytes for potential network streaming.
    """
    global _is_playing 
    if not speech.strip():
        return b""

    communicate = edge_tts.Communicate(speech, voice)
    
    # Collect all chunks into buffer (MP3 requires complete binary for decoding)
    buffer = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk['type'] == 'audio':
            buffer.write(chunk['data'])
    
    buffer.seek(0)
    return buffer.getvalue()