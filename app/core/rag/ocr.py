# app/core/rag/ocr.py
import base64
import io
from PIL import Image
import pytesseract

from app.utils.logging_config import get_logger

logger = get_logger(__name__)


def extract_text_from_base64(image_b64: str) -> str:
    try:
        image_bytes = base64.b64decode(image_b64)
        image = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception:
        logger.exception("OCR extraction failed")
        return ""