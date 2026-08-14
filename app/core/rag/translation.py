# app/core/rag/translation.py
from deep_translator import GoogleTranslator
from langdetect import detect, LangDetectException

from app.utils.logging_config import get_logger

logger = get_logger(__name__)


def detect_language(text: str) -> str:
    try:
        lang = detect(text)
        logger.info("Detected language: %s | text_preview=%s", lang, text[:50])
        return lang
    except LangDetectException:
        logger.warning("Language detection failed, defaulting to 'en'")
        return "en"


def to_english(text: str, source_lang: str) -> str:
    if source_lang == "en":
        return text
    logger.info("Translating to English | source=%s | chars=%d", source_lang, len(text))
    try:
        result = GoogleTranslator(source="auto", target="english").translate(text)
        logger.info("✓ Translation to English completed | chars=%d", len(result))
        return result
    except Exception:
        logger.exception("Translation to English failed, falling back to original text")
        return text


def from_english(text: str, target_lang: str) -> str:
    if target_lang == "en":
        return text
    logger.info("Translating from English | target=%s | chars=%d", target_lang, len(text))
    try:
        result = GoogleTranslator(source="english", target=target_lang).translate(text)
        logger.info("✓ Translation to %s completed | chars=%d", target_lang, len(result))
        return result
    except Exception:
        logger.exception("Translation back to source language failed, returning English")
        return text