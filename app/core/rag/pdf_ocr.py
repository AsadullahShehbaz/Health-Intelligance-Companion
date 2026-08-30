import base64
import io
from typing import List

import pypdfium2 as pdfium
from pypdf import PdfReader

from app.config import settings
from app.core.rag.ocr import run_vision_extraction
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


def parse_pdf_base64(raw_b64_string: str) -> bytes:
    """Strip data URI prefix and return the raw PDF bytes."""
    if not raw_b64_string:
        logger.info("PDF decode skipped — empty input")
        return b""

    normalized = raw_b64_string.strip()
    if ";base64," in normalized:
        header, payload = normalized.split(";base64,", 1)
        normalized = payload
        logger.debug("PDF payload had data URI prefix | header=%s", header)

    try:
        decoded = base64.b64decode(normalized, validate=True)
        logger.info("PDF base64 decoded successfully | bytes=%d", len(decoded))
        return decoded
    except Exception:
        logger.warning("Failed to decode PDF base64 payload | input_len=%d", len(normalized))
        return b""


def extract_native_text(pdf_bytes: bytes, max_pages: int) -> List[str]:
    """Return per-page text extracted natively from the PDF."""
    pages: List[str] = []
    if not pdf_bytes:
        logger.warning("Native PDF extraction skipped — empty bytes")
        return pages

    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        logger.info("Native PDF extraction attempt | pages_available=%d | max_pages=%d", len(reader.pages), max_pages)
        for idx, page in enumerate(reader.pages[:max_pages]):
            try:
                page_text = page.extract_text() or ""
                pages.append(page_text)
                logger.debug("Native page extraction | page=%d | chars=%d", idx + 1, len(page_text))
            except Exception:
                logger.warning("Page %s native PDF extraction failed", idx + 1)
                pages.append("")
        return pages
    except Exception:
        logger.warning("PDF parsing failed during native extraction | bytes=%d", len(pdf_bytes), exc_info=True)
        return []


def rasterize_page(pdf_bytes: bytes, page_index: int) -> bytes:
    """Render selected page to a PNG for OCR fallback."""
    try:
        logger.debug("Rasterizing PDF page for OCR fallback | page=%d | input_bytes=%d", page_index + 1, len(pdf_bytes))
        pdf = pdfium.PdfDocument(io.BytesIO(pdf_bytes))
        page = pdf.get_page(page_index)
        bitmap = page.render(scale=2.0)
        png_image = bitmap.to_pil()
        buffer = io.BytesIO()
        png_image.save(buffer, format="PNG")
        png_bytes = buffer.getvalue()
        logger.info("PDF page rasterized successfully | page=%d | png_bytes=%d", page_index + 1, len(png_bytes))
        return png_bytes
    except Exception:
        logger.warning("PDF page rasterization failed for page %s", page_index + 1, exc_info=True)
        return b""


def extract_text_from_pdf_base64(pdf_b64: str) -> str:
    """Extract text from a PDF using native parsing with a Groq OCR fallback."""
    if not pdf_b64:
        logger.info("PDF OCR skipped — empty pdf_base64")
        return ""

    logger.info(
        "Starting PDF extraction | pdf_input_len=%d | max_pages=%d | max_vision_pages=%d | min_native_chars=%d",
        len(pdf_b64),
        settings.PDF_MAX_PAGES,
        settings.PDF_MAX_VISION_PAGES,
        settings.PDF_NATIVE_TEXT_MIN_CHARS,
    )

    try:
        pdf_bytes = parse_pdf_base64(pdf_b64)
        if not pdf_bytes:
            logger.warning("PDF payload empty or invalid base64 | bytes=%d", len(pdf_bytes))
            return ""

        max_size_bytes = settings.PDF_MAX_SIZE_MB * 1024 * 1024
        if len(pdf_bytes) > max_size_bytes:
            logger.warning(
                "PDF exceeds max size | size_bytes=%d | max_bytes=%d | max_mb=%s",
                len(pdf_bytes),
                max_size_bytes,
                settings.PDF_MAX_SIZE_MB,
            )
            return ""

        reader = None
        try:
            reader = PdfReader(io.BytesIO(pdf_bytes))
        except Exception:
            logger.warning("PDF unreadable or encrypted | bytes=%d", len(pdf_bytes), exc_info=True)
            return ""

        page_count = len(getattr(reader, "pages", []) or [])
        logger.info("PDF parsed successfully | total_pages=%d | bytes=%d", page_count, len(pdf_bytes))

        if not page_count:
            logger.warning("PDF contains no pages")
            return ""

        max_pages = min(page_count, settings.PDF_MAX_PAGES)
        logger.info("Processing PDF pages | total=%d | capped=%d", page_count, max_pages)

        page_results: List[str] = []
        vision_calls = 0

        for page_number in range(max_pages):
            page = reader.pages[page_number]
            try:
                native_text = (page.extract_text() or "").strip()
            except Exception:
                logger.warning("Page %s extraction failed", page_number + 1, exc_info=True)
                native_text = ""

            logger.debug(
                "PDF page evaluation | page=%d | native_chars=%d | vision_calls_used=%d | vision_cap=%d",
                page_number + 1,
                len(native_text),
                vision_calls,
                settings.PDF_MAX_VISION_PAGES,
            )

            if len(native_text) >= settings.PDF_NATIVE_TEXT_MIN_CHARS:
                logger.info("Using native text for page %d | chars=%d", page_number + 1, len(native_text))
                page_results.append(f"--- Page {page_number + 1} ---\n{native_text}")
                continue

            if vision_calls >= settings.PDF_MAX_VISION_PAGES:
                if native_text:
                    logger.info("Page %d has weak native text but vision cap reached; keeping native text only", page_number + 1)
                    page_results.append(f"--- Page {page_number + 1} ---\n{native_text}")
                else:
                    logger.info("Page %d has no usable text and vision cap reached; skipping", page_number + 1)
                continue

            png_bytes = rasterize_page(pdf_bytes, page_number)
            if not png_bytes:
                if native_text:
                    logger.info("Page %d rasterization failed; falling back to native text only", page_number + 1)
                    page_results.append(f"--- Page {page_number + 1} ---\n{native_text}")
                else:
                    logger.warning("Page %d had no native text and rasterization failed", page_number + 1)
                continue

            vision_calls += 1
            png_b64 = base64.b64encode(png_bytes).decode("ascii")
            logger.info("Vison OCR fallback triggered | page=%d | fallback_call=%d", page_number + 1, vision_calls)
            fallback_text = run_vision_extraction(png_b64, "image/png")
            final_page_text = fallback_text or native_text or "[unclear]"
            page_results.append(f"--- Page {page_number + 1} ---\n{final_page_text}")

        joined = "\n\n".join(page_results).strip()
        logger.info(
            "PDF extraction finished | total_output_chars=%d | pages_processed=%d | vision_calls_used=%d",
            len(joined),
            len(page_results),
            vision_calls,
        )
        return joined

    except Exception:
        logger.exception("PDF extraction failed")
        return ""
