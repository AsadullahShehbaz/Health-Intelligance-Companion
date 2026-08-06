# app/core/rag/qdrant_store.py

from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

from app.config import settings
from app.core.rag.embedder import get_embedder
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

embedder = get_embedder()

client = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY,
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

    try:
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

        results = client.query_points(
            collection_name=COLLECTION,
            query=vector,
            query_filter=query_filter,
            limit=top_k,
            with_payload=True,
            score_threshold=0.3,
        )

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

    except Exception:
        logger.exception("Qdrant retrieval failed.")
        raise