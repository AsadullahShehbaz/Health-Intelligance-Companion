import base64

import pytest

from app.core.rag.pdf_ocr import extract_text_from_pdf_base64, parse_pdf_base64


@pytest.mark.unit
def test_parse_pdf_base64_strips_data_uri():
    raw = "data:application/pdf;base64,SGVsbG8="
    assert parse_pdf_base64(raw) == b"Hello"


@pytest.mark.unit
def test_extract_text_from_pdf_base64_returns_native_text(monkeypatch):
    class _FakePage:
        def extract_text(self):
            return "Patient: Ali\nHemoglobin: 12.5 g/dL"

    class _FakeReader:
        def __init__(self, *args, **kwargs):
            self.pages = [_FakePage()]

    monkeypatch.setattr("app.core.rag.pdf_ocr.PdfReader", _FakeReader)

    payload = base64.b64encode(b"fake-pdf-bytes")
    result = extract_text_from_pdf_base64(payload.decode("ascii"))

    assert "Patient: Ali" in result
    assert "Hemoglobin: 12.5 g/dL" in result


@pytest.mark.unit
def test_extract_text_from_pdf_base64_uses_vision_fallback(monkeypatch):
    class _FakePage:
        def extract_text(self):
            return "[unclear]"

    class _FakeReader:
        def __init__(self, *args, **kwargs):
            self.pages = [_FakePage()]

    monkeypatch.setattr("app.core.rag.pdf_ocr.PdfReader", _FakeReader)
    monkeypatch.setattr("app.core.rag.pdf_ocr.rasterize_page", lambda *args, **kwargs: b"png-bytes")
    monkeypatch.setattr("app.core.rag.pdf_ocr.run_vision_extraction", lambda *args, **kwargs: "Vision fallback extracted text")

    payload = base64.b64encode(b"fake-pdf-bytes")
    result = extract_text_from_pdf_base64(payload.decode("ascii"))

    assert "Vision fallback extracted text" in result


@pytest.mark.unit
def test_extract_text_from_pdf_base64_rejects_large_pdf(monkeypatch):
    monkeypatch.setattr("app.core.rag.pdf_ocr.settings.PDF_MAX_SIZE_MB", 0)
    payload = base64.b64encode(b"fake-pdf-bytes")
    assert extract_text_from_pdf_base64(payload.decode("ascii")) == ""


@pytest.mark.unit
def test_extract_text_from_pdf_base64_handles_corrupt_pdf(monkeypatch):
    def _boom(*args, **kwargs):
        raise ValueError("bad pdf")

    monkeypatch.setattr("app.core.rag.pdf_ocr.PdfReader", _boom)
    payload = base64.b64encode(b"not-a-valid-pdf")
    assert extract_text_from_pdf_base64(payload.decode("ascii")) == ""
