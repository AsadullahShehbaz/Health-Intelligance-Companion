# app/core/voice.py
import io
import asyncio
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
import edge_tts
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

_playback_lock = asyncio.Lock()
_is_playing = False 

def stop_audio():
    global _is_playing
    sd.stop()
    _is_playing = False
    logger.info("Playback stopped by request.")
     
# Initialize recognizer instance
_recognizer = sr.Recognizer()

def capture_and_transcribe(pause_threshold: float = 2.0) -> str:
    """
    Captures live audio input from local microphone and converts to text using Google STT.
    """
    with sr.Microphone() as source:
        logger.info("Listening for audio input...")
        _recognizer.adjust_for_ambient_noise(source)
        _recognizer.pause_threshold = pause_threshold
        
        audio = _recognizer.listen(source)
        logger.info("Processing STT...")
        
        stt_text = _recognizer.recognize_google(audio)
        logger.info("Transcribed text: %s", stt_text)
        return stt_text


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