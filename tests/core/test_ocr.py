"""Unit tests for app/core/rag/ocr.py — OCR extraction with mocked pytesseract."""
import pytest

from app.core.rag.ocr import extract_text_from_base64


@pytest.mark.unit
def test_ocr_empty_string_returns_empty():
    assert extract_text_from_base64("") == ""


@pytest.mark.unit
def test_ocr_none_returns_empty():
    assert extract_text_from_base64(None) == ""


@pytest.mark.unit
def test_ocr_extracts_text(monkeypatch):
    """With mocked pytesseract and Image.open, returns the extracted text."""
    from types import SimpleNamespace
    monkeypatch.setattr("app.core.rag.ocr.Image.open", lambda buf: SimpleNamespace(size=(1,1), mode="RGB"))
    monkeypatch.setattr("app.core.rag.ocr.pytesseract.image_to_string", lambda img: "Diagnosis: Hypertension")

    result = extract_text_from_base64("aGVsbG8=")  # valid base64
    assert result == "Diagnosis: Hypertension"


@pytest.mark.unit
def test_ocr_handles_invalid_base64():
    """Invalid base64 should not raise — returns empty string."""
    result = extract_text_from_base64("!!!not-base64!!!")
    assert result == ""


@pytest.mark.unit
def test_ocr_handles_pytesseract_error(monkeypatch):
    """If pytesseract raises, the error is caught and empty string returned."""
    def _boom(img):
        raise RuntimeError("tesseract not installed")

    monkeypatch.setattr("app.core.rag.ocr.pytesseract.image_to_string", _boom)
    assert extract_text_from_base64("aGVsbG8=") == ""
