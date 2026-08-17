Here are your markdown notes for understanding `edge-tts` syntax and logic:

---

# 🎙️ edge-tts — Syntax & Logic Notes

## 1. What is edge-tts?

`edge-tts` is a Python library that reverse-engineers the **free neural text-to-speech engine** built into Microsoft Edge browser. It sends text to Microsoft's servers and returns audio — **no API key required**.

> **Key insight:** It mimics how Edge browser itself requests speech. That's why no authentication is needed.

---

## 2. Your App's Data Flow

```
🎤 Mic → 📝 SpeechRecognition (STT) → 🧠 ChatGroq (LLM) → 🔊 edge-tts → 🎧 pygame
```

| Step | Tool | Job |
|------|------|-----|
| 1 | `speech_recognition` | Captures voice, converts to text |
| 2 | `ChatGroq` | Generates AI response |
| 3 | `edge_tts.Communicate()` | Converts response text to speech |
| 4 | `pygame` | Plays the MP3 audio |

---

## 3. Core Syntax Breakdown

### Step 1: Create a `Communicate` object

```python
import edge_tts

communicate = edge_tts.Communicate(
    text="Hello, I am your voice agent!",
    voice="en-US-AriaNeural"
)
```

| Parameter | Description |
|-----------|-------------|
| `text` | The string to speak. Supports long multi-sentence text. |
| `voice` | Voice ID. Must be a valid Microsoft Edge voice name. |

> `Communicate()` only **prepares** the request. It does NOT download audio yet.

---

### Step 2: Save audio to file

```python
await communicate.save("response.mp3")
```

- `.save()` is an **async** method — that's why `await` is required.
- It **streams audio chunks** from Microsoft's server and writes to disk.
- Async prevents your program from freezing during the network call.

---

## 4. Full `tts()` Function — Line by Line

```python
import edge_tts
import asyncio
import pygame

async def tts(speech: str):
    # 1. Create the TTS job
    communicate = edge_tts.Communicate(speech, voice="en-US-AriaNeural")
    
    # 2. Download & save audio (network I/O — async!)
    await communicate.save("response.mp3")
    
    # 3. Initialize pygame audio engine
    pygame.mixer.init()
    
    # 4. Load MP3 into memory
    pygame.mixer.music.load("response.mp3")
    
    # 5. Start playback (non-blocking!)
    pygame.mixer.music.play()
    
    # 6. Block until audio finishes
    while pygame.mixer.music.get_busy():
        await asyncio.sleep(0.1)
```

### Why the `while` loop is critical

`pygame.mixer.music.play()` is **non-blocking** — it starts playing and immediately returns. Without the loop, your script would exit and **cut off the audio mid-sentence**.

`asyncio.sleep(0.1)` yields control so other async tasks can run while waiting.

---

## 5. Common Voice IDs

| Voice ID | Accent / Gender | Best For |
|----------|----------------|----------|
| `en-US-AriaNeural` | American female | Assistants (default) |
| `en-US-GuyNeural` | American male | Professional tone |
| `en-GB-SoniaNeural` | British female | Crisp, articulate |
| `en-GB-RyanNeural` | British male | Confident tone |
| `en-AU-NatashaNeural` | Australian female | Friendly |
| `en-IN-NeerjaNeural` | Indian female | Expressive |

**List all voices:**
```bash
edge-tts --list-voices
```

---

## 6. Advanced Options (SSML)

### Speech Rate (speed)

```python
text = '<speak><prosody rate="+20%">I speak faster now!</prosody></speak>'
communicate = edge_tts.Communicate(text, voice="en-US-AriaNeural")
```

- `"-"` values = slower (e.g., `"-50%"`)
- `"+"` values = faster (e.g., `"+50%"`)

### Volume

```python
text = '<speak><prosody volume="+20dB">I am louder!</prosody></speak>'
```

### Pitch

```python
text = '<speak><prosody pitch="+10Hz">Higher pitch voice</prosody></speak>'
```

---

## 7. Streaming (No File Save)

Instead of saving to disk, stream audio chunks directly — **lower latency**:

```python
async def stream_tts(text):
    communicate = edge_tts.Communicate(text, voice="en-US-AriaNeural")
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data = chunk["data"]
            # Feed audio_data to your player chunk-by-chunk
```

---

## 8. Common Pitfalls & Fixes

| Problem | Cause | Fix |
|---------|-------|-----|
| `RuntimeError: Event loop is closed` | Calling `asyncio.run()` inside an already running async loop | In sync `main()`, use `asyncio.run()`. In async `main()`, just `await tts()` |
| Audio doesn't play / cuts off | Missing busy-wait loop or `init()` after `load()` | Always include `while get_busy()` loop. Call `pygame.mixer.init()` before `.load()` |
| Garbled / silent audio | Invalid voice ID | Verify voice exists: `edge-tts --list-voices \| grep "your-voice"` |
| File clutter | Saving MP3s to working directory | Use `tempfile.NamedTemporaryFile()` for auto-cleanup |

---

## 9. Clean Production Version

```python
import speech_recognition as sr
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage
import edge_tts, asyncio, pygame, tempfile, os

llm = ChatGroq(model_name="openai/gpt-oss-20b")

async def tts(speech: str, voice: str = "en-US-AriaNeural"):
    # Use temp file to avoid clutter
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tmp_path = tmp.name
    
    await edge_tts.Communicate(speech, voice=voice).save(tmp_path)
    
    pygame.mixer.init()
    pygame.mixer.music.load(tmp_path)
    pygame.mixer.music.play()
    
    while pygame.mixer.music.get_busy():
        await asyncio.sleep(0.1)
    
    pygame.mixer.music.unload()
    os.remove(tmp_path)  # Clean up

def main():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        r.pause_threshold = 2
        
        print("Say something...")
        audio = r.listen(source)
        
        stt = r.recognize_google(audio)
        print("You said:", stt)
        
        result = llm.invoke([
            SystemMessage(content="You are an expert voice agent..."),
            {"role": "user", "content": stt}
        ])
        
        print(result.content)
        asyncio.run(tts(result.content))

if __name__ == "__main__":
    main()
```

---

## 10. Quick Reference

```python
# Basic usage
communicate = edge_tts.Communicate(text, voice="en-US-AriaNeural")
await communicate.save("output.mp3")

# With SSML prosody
text = '<speak><prosody rate="+20%" pitch="+10Hz">Hello!</prosody></speak>'

# Streaming
async for chunk in communicate.stream():
    if chunk["type"] == "audio":
        process(chunk["data"])
```

---