# app/core/rag/qdrant_store.py

import time

from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

from app.config import settings
from app.core.rag.embedder import get_embedder
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

embedder = get_embedder()

# Qdrant Cloud free tier autosuspends an idle cluster; the first query after
# idle has to wake it up, which can blow past httpx's default read timeout.
# A generous timeout + a retry mirrors the Neon autosuspend handling in
# agent_service.py.
_QDRANT_TIMEOUT = 60
_QDRANT_RETRIES = 1
_QDRANT_RETRY_DELAY = 1.0

client = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY,
    timeout=_QDRANT_TIMEOUT,
)

COLLECTION = "health_knowledge"


def retrieve(
    query: str,
    top_k: int = 5,
    category: str | None = None,
) -> list[dict]:
    """
    Retrieve the most relevant medical documents from Qdrant.
    """

    logger.info(
        "Searching Qdrant | collection=%s | top_k=%d",
        COLLECTION,
        top_k,
    )

    # Generate embedding
    vector = embedder.encode(
        query,
        normalize_embeddings=True,
    ).tolist()

    query_filter = None

    if category:
        logger.debug("Applying category filter: %s", category)

        query_filter = Filter(
            must=[
                FieldCondition(
                    key="category",
                    match=MatchValue(value=category),
                )
            ]
        )

    # Retry transient network errors (autosuspend wake, throttling). If the
    # cluster is genuinely down this re-raises after the last attempt and the
    # calling tool (retrieve_medical_knowledge) degrades gracefully instead of
    # killing the agent.
    for attempt in range(_QDRANT_RETRIES + 1):
        try:
            results = client.query_points(
                collection_name=COLLECTION,
                query=vector,
                query_filter=query_filter,
                limit=top_k,
                with_payload=True,
                score_threshold=0.3,
            )
            break
        except Exception as e:
            if attempt >= _QDRANT_RETRIES:
                logger.exception("Qdrant query failed after %d attempts", attempt + 1)
                raise
            logger.warning(
                "Transient Qdrant error (attempt %d/%d), retrying: %s",
                attempt + 1,
                _QDRANT_RETRIES,
                e,
            )
            time.sleep(_QDRANT_RETRY_DELAY)

    docs = [
        {
            "text": r.payload.get("text", ""),
            "source": r.payload.get("source", ""),
            "category": r.payload.get("category", ""),
            "score": r.score,
        }
        for r in results.points
    ]

    logger.info(
        "Qdrant retrieval completed | retrieved=%d documents",
        len(docs),
    )

    return docs