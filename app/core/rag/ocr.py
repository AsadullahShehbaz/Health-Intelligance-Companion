# app/core/rag/ocr.py
import base64
import io
from PIL import Image
import pytesseract

from app.utils.logging_config import get_logger

logger = get_logger(__name__)


def extract_text_from_base64(image_b64: str) -> str:
    if not image_b64:
        logger.info("OCR skipped — empty image_base64")
        return ""
    logger.info("▶ OCR extraction started | b64_len=%d", len(image_b64))
    try:
        image_bytes = base64.b64decode(image_b64)
        image = Image.open(io.BytesIO(image_bytes))
        logger.info("Image loaded | size=%s | mode=%s", image.size, image.mode)
        text = pytesseract.image_to_string(image)
        result = text.strip()
        logger.info("✓ OCR extraction completed | chars=%d", len(result))
        return result
    except Exception:
        logger.exception("OCR extraction failed")
        return ""