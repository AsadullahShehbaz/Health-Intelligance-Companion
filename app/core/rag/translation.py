# app/core/rag/translation.py
from deep_translator import GoogleTranslator
from langdetect import detect, LangDetectException

from app.utils.logging_config import get_logger

logger = get_logger(__name__)


def detect_language(text: str) -> str:
    try:
        return detect(text)
    except LangDetectException:
        return "en"


def to_english(text: str, source_lang: str) -> str:
    if source_lang == "en":
        return text
    try:
        return GoogleTranslator(source="auto", target="english").translate(text)
    except Exception:
        logger.exception("Translation to English failed, falling back to original text")
        return text


def from_english(text: str, target_lang: str) -> str:
    if target_lang == "en":
        return text
    try:
        return GoogleTranslator(source="english", target=target_lang).translate(text)
    except Exception:
        logger.exception("Translation back to source language failed, returning English")
        return text