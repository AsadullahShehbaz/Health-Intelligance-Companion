"""
test-ocr.py — run the OCR + agent flow against a live backend.

Sends app/tests/sample-report.png as image_base64 to POST /agent/invoke
(just like the frontend does) and prints the extracted OCR text plus the
assistant's answer.

Run directly against a running backend (same as the other test scripts):

    conda activate ft-project
    python app/tests/test-ocr.py ["<optional query>"]

Defaults to the same query used to reproduce the original bug: "what it mean".
"""
import base64
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo root, so `import app` works

from fastapi.testclient import TestClient

from app.main import app
from app.core.rag.ocr import extract_text_from_base64

IMAGE_PATH = Path(__file__).parent / "sample-report.png"
QUERY = sys.argv[1] if len(sys.argv) > 1 else "what it mean"

# Raw base64, no `data:image/...;base64,` prefix — exactly what the
# frontend sends (see frontend/src/utils/image.js) and what
# app/core/rag/ocr.py expects to b64decode.
image_b64 = base64.b64encode(IMAGE_PATH.read_bytes()).decode("ascii")

print("=" * 60)
print("OCR PREVIEW (what the agent will read from the image)")
print("=" * 60)
ocr_text = extract_text_from_base64(image_b64)
print(f"Extracted {len(ocr_text)} chars:")
print(ocr_text[:2000] if ocr_text else "(no text extracted)")
print("=" * 60)

# Entering the context manager runs the FastAPI lifespan, which sets up the
# LangGraph checkpointer/store tables (deferred from import time since Week 6
# moved them into app/db/lifespan.py) plus init_models/embedder.
with TestClient(app) as client:

    print(f"Posting to /agent/invoke | query={QUERY!r} | image_bytes={len(image_b64)}")
    response = client.post(
        "/agent/invoke",
        json={
            "patient_id": "test-ocr-patient",
            "query": QUERY,
            "thread_id": "test-ocr-conversation",
            "image_base64": image_b64,
        },
    )

print("Status:", response.status_code)
print("=" * 60)
print("ANSWER")
print("=" * 60)

data = response.json()
print(data.get("answer"))
print("\n— detected_lang:", data.get("detected_lang"))
print("— needs_rag:", data.get("needs_rag"))
print("— retrieval_decision:", data.get("retrieval_decision"))
print("— save_memory:", data.get("save_memory"))
print("— sources:", data.get("sources"))
