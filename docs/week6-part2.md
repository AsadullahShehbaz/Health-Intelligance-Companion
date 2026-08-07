Before the code — a quick scope flag, then I'll build it. TrOCR (~1.3GB model) + Whisper (even the small/int8 faster-whisper build) are real model loads on top of your existing BioMistral GGUF and MiniLM embedder — given the disk constraints you documented back in Week 4 (D: drive had ~10.7GB free) and that you're now inside the final stretch before Aug 30, worth checking free disk space before running this. If it's tight, `faster-whisper`'s `tiny` or `base` model and TrOCR's `base` (not `large`) checkpoints keep this to a few hundred MB total instead of gigabytes.

I'm keeping STT/TrOCR as **deterministic preprocessing nodes** and TTS as a **deterministic post-processing node** — consistent with the Week 6 decision that OCR/voice/PDF aren't agent-decided tools, since "was audio attached" and "was an image attached" are facts from the request, not judgment calls.

## Core modules

```python
# app/core/rag/voice.py
"""Speech-to-text via faster-whisper (CPU-friendly, int8 quantized)."""
from faster_whisper import WhisperModel
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

logger.info("Loading Whisper STT model...")
_stt_model = WhisperModel("base", device="cpu", compute_type="int8")
logger.info("Whisper STT model loaded.")


def transcribe_audio(audio_bytes: bytes) -> tuple[str, str]:
    """Returns (transcript, detected_language_code)."""
    import tempfile, os

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_bytes)
            tmp_path = f.name

        segments, info = _stt_model.transcribe(tmp_path, beam_size=5)
        transcript = " ".join(seg.text.strip() for seg in segments).strip()
        return transcript, info.language
    except Exception:
        logger.exception("STT transcription failed")
        return "", "en"
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
```

```python
# app/core/rag/tts.py
"""Text-to-speech via pyttsx3 — fully offline, no API key, matches the
local-only inference philosophy of the rest of the pipeline."""
import base64
import io
import tempfile
import os
import pyttsx3
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


def synthesize_speech(text: str, lang: str = "en") -> str | None:
    """Returns base64-encoded WAV audio, or None on failure."""
    if not text.strip():
        return None

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            tmp_path = f.name

        engine = pyttsx3.init()
        engine.setProperty("rate", 165)

        # prefer an Urdu-capable voice if one is installed; otherwise default
        if lang != "en":
            for voice in engine.getProperty("voices"):
                if lang in (voice.languages[0].decode(errors="ignore") if voice.languages else "").lower():
                    engine.setProperty("voice", voice.id)
                    break

        engine.save_to_file(text, tmp_path)
        engine.runAndWait()

        with open(tmp_path, "rb") as f:
            audio_bytes = f.read()
        return base64.b64encode(audio_bytes).decode()
    except Exception:
        logger.exception("TTS synthesis failed")
        return None
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
```

```python
# app/core/rag/trocr.py
"""Handwritten prescription reader via TrOCR (base, handwritten checkpoint)."""
import base64
import io
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

logger.info("Loading TrOCR handwritten model...")
_processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
_model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten")
logger.info("TrOCR model loaded.")


def read_handwritten_prescription(image_b64: str) -> str:
    try:
        image_bytes = base64.b64decode(image_b64)
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        pixel_values = _processor(images=image, return_tensors="pt").pixel_values
        generated_ids = _model.generate(pixel_values, max_length=128)
        text = _processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return text.strip()
    except Exception:
        logger.exception("TrOCR extraction failed")
        return ""
```

TrOCR is line-level — it reads one line of handwriting well but doesn't segment a full prescription photo into lines on its own. For a realistic demo, either crop to one line before calling this, or accept it'll do best on short/cropped prescription snippets rather than a full messy multi-line scrawl. Worth testing on 2-3 real sample images before relying on it live.

## State, schema, and input processor updates

```python
# app/agent/state.py — add these fields
class AgentState(TypedDict):
    # ...existing fields...
    has_audio: bool
    audio_base64: Optional[str]
    is_handwritten: bool          # True routes image through TrOCR instead of Tesseract
    tts_audio_base64: Optional[str]
```

```python
# app/schemas/agent.py — extend AgentRequest/AgentResponse
class AgentRequest(BaseModel):
    patient_id: str
    query: str = ""
    image_base64: Optional[str] = None
    is_handwritten: bool = False          # frontend sets this when user picks "prescription photo"
    audio_base64: Optional[str] = None
    input_modality: Literal["text", "image", "voice"] = "text"
    want_voice_response: bool = False     # frontend requests TTS back


class AgentResponse(BaseModel):
    answer: str
    detected_lang: str
    needs_rag: bool = False
    save_memory: bool = False
    audio_base64: Optional[str] = None    # populated if want_voice_response was set
```

```python
# app/agent/nodes/input_processor_node.py — replaces ocr_node
from app.agent.state import AgentState
from app.core.rag.ocr import extract_text_from_base64
from app.core.rag.trocr import read_handwritten_prescription
from app.core.rag.voice import transcribe_audio
import base64


def input_processor_node(state: AgentState) -> AgentState:
    raw = state.get("raw_input", "")

    if state.get("has_audio") and state.get("audio_base64"):
        audio_bytes = base64.b64decode(state["audio_base64"])
        transcript, detected_lang = transcribe_audio(audio_bytes)
        if transcript:
            raw = transcript
            state["detected_lang"] = detected_lang  # skip langdetect, Whisper already knows

    if state.get("has_image") and state.get("image_base64"):
        if state.get("is_handwritten"):
            extracted = read_handwritten_prescription(state["image_base64"])
            label = "Prescription"
        else:
            extracted = extract_text_from_base64(state["image_base64"])
            label = "Image OCR"
        if extracted:
            raw = f"{raw}\n[{label}]: {extracted}".strip()

    state["raw_input"] = raw
    return state
```

```python
# app/agent/nodes/tts_node.py — new, appended after translate_out
from app.agent.state import AgentState
from app.core.rag.tts import synthesize_speech


def tts_node(state: AgentState) -> AgentState:
    if not state.get("want_voice_response"):
        state["tts_audio_base64"] = None
        return state
    state["tts_audio_base64"] = synthesize_speech(
        state["final_response"], state.get("detected_lang", "en")
    )
    return state
```

`want_voice_response` needs adding to `AgentState` too — same pattern as the other flags above.

## Graph wiring

```python
# app/agent/graph.py — swap ocr_node for input_processor_node, add tts_node at the end
from app.agent.nodes.input_processor_node import input_processor_node
from app.agent.nodes.tts_node import tts_node
# ...other imports unchanged...

def build_health_agent():
    graph = StateGraph(AgentState)

    graph.add_node("input_processor", input_processor_node)   # was "ocr"
    graph.add_node("translate_in", translate_in_node)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(TOOLS))
    graph.add_node("translate_out", translate_out_node)
    graph.add_node("tts", tts_node)                             # new

    graph.set_entry_point("input_processor")
    graph.add_edge("input_processor", "translate_in")
    graph.add_edge("translate_in", "agent")
    graph.add_conditional_edges("agent", _route_after_agent, {"tools": "tools", "translate_out": "translate_out"})
    graph.add_edge("tools", "agent")
    graph.add_edge("translate_out", "tts")                      # new
    graph.add_edge("tts", END)

    return graph.compile(checkpointer=checkpointer, store=store)
```

## Service layer update

```python
# app/services/agent_service.py — update _build_initial_state and the return
def _build_initial_state(req: AgentRequest) -> dict:
    return {
        # ...existing fields...
        "has_audio": req.audio_base64 is not None,
        "audio_base64": req.audio_base64,
        "is_handwritten": req.is_handwritten,
        "want_voice_response": req.want_voice_response,
        "tts_audio_base64": None,
    }

# in run_agent(), add to the returned AgentResponse:
audio_base64=result.get("tts_audio_base64"),
```

## Dependencies

```bash
pip install faster-whisper pyttsx3 transformers --break-system-packages
```

`pytesseract`/Tesseract binary stays for printed-text OCR (prescriptions typed by a pharmacy) — TrOCR is specifically the handwritten path, on `is_handwritten=True`.

## One thing worth deciding now, given your timeline

You have three new model loads happening at startup (Whisper, TrOCR, plus your existing BioMistral + MiniLM). On a CPU-only machine, startup time and RAM pressure compound — worth running `uvicorn` once after this change and timing how long it takes to become ready before you build the frontend around it. If startup is uncomfortably slow, lazy-loading TrOCR/Whisper on first use (rather than at import time) instead of eagerly at boot is a quick fix worth having ready.

Want me to also wire the React frontend side (mic button for voice input, prescription-photo upload toggle, audio playback for TTS response) to match these new request fields?