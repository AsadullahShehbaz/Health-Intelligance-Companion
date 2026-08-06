# app/core/rag/corrective_rag.py

from serpapi import GoogleSearch

from app.config import settings
from app.core.rag.qdrant_store import retrieve
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

RELEVANCE_THRESHOLD = 0.5
AMBIGUOUS_THRESHOLD = 0.35


def evaluate_relevance(docs: list[dict]) -> tuple[str, float]:
    """
    Evaluate the quality of retrieved documents.
    """

    if not docs:
        logger.warning("No documents retrieved from Qdrant.")
        return "incorrect", 0.0

    scores = [d["score"] for d in docs]
    avg_score = sum(scores) / len(scores)
    max_score = max(scores)

    logger.info(
        "Retrieval evaluation completed | max_score=%.3f | avg_score=%.3f",
        max_score,
        avg_score,
    )

    if max_score >= RELEVANCE_THRESHOLD:
        logger.info("Retrieval classified as CORRECT.")
        return "correct", avg_score

    if avg_score >= AMBIGUOUS_THRESHOLD:
        logger.warning("Retrieval classified as AMBIGUOUS.")
        return "ambiguous", avg_score

    logger.warning("Retrieval classified as INCORRECT.")
    return "incorrect", avg_score


def web_search_fallback(query: str) -> list[dict]:
    """
    Google Search fallback using SerpAPI.
    """

    logger.info("Starting SerpAPI fallback search...")

    try:
        params = {
            "engine": "google",
            "q": f"medical {query}",
            "api_key": settings.SERP_API_KEY,
            "num": 3,
            "gl": "us",
            "hl": "en",
            "safe": "active",
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        docs = []

        for item in results.get("organic_results", []):
            docs.append(
                {
                    "text": item.get("snippet", ""),
                    "source": item.get("link", ""),
                    "category": "web",
                    "score": 0.5,
                    "title": item.get("title", ""),
                }
            )

        logger.info(
            "SerpAPI returned %d web documents.",
            len(docs),
        )

        return docs

    except Exception:
        logger.exception("SerpAPI fallback failed.")
        return []


def corrective_retrieve(query: str, top_k: int = 5) -> dict:
    """
    Complete Corrective RAG retrieval pipeline.
    """

    logger.info("Starting Corrective RAG pipeline.")

    docs = retrieve(query, top_k=top_k)

    logger.info("Retrieved %d documents from Qdrant.", len(docs))

    decision, avg_score = evaluate_relevance(docs)

    if decision == "incorrect":
        logger.warning(
            "Low retrieval quality detected. Replacing context with web search results."
        )
        docs = web_search_fallback(query) + docs

    elif decision == "ambiguous":
        logger.warning(
            "Ambiguous retrieval detected. Augmenting context with web search results."
        )
        docs = docs + web_search_fallback(query)

    logger.info(
        "Corrective RAG completed | decision=%s | avg_score=%.3f | final_docs=%d",
        decision,
        avg_score,
        len(docs[:5]),
    )

    return {
        "docs": docs[:5],
        "decision": decision,
        "avg_score": round(avg_score, 3),
    }