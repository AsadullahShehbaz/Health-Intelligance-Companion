# app/core/rag/embedder.py

from sentence_transformers import SentenceTransformer

from app.config import settings
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

_embedder: SentenceTransformer | None = None


def get_embedder() -> SentenceTransformer:
    """
    Return a singleton SentenceTransformer instance.
    The model is loaded only once during the application's lifetime.
    """
    global _embedder

    if _embedder is None:
        logger.info("Loading embedding model...")
        _embedder = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2",
            token=settings.HF_TOKEN,
        )
        logger.info("Embedding model loaded.")

    return _embedder