# app/core/rag/rag_tool.py
"""Direct RAG tool — streamlined vector retrieval without CRAG evaluation loops."""

import logging
from typing import List, Dict, Any

from app.core.rag.qdrant_store import retrieve

logger = logging.getLogger(__name__)


def perform_direct_rag(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Executes direct vector retrieval from the local knowledge base without
    corrective re-ranking or query rewriting loops.

    Args:
        query: The user's medical/health query.
        top_k: Number of top documents to retrieve (default 3).

    Returns:
        List of dictionaries with keys: title, text, score, source.
    """
    logger.info("▶ Direct RAG Search | query=%s", query[:80])
    try:
        # Use the Qdrant retriever directly
        docs = retrieve(query, top_k=top_k)

        results = []
        for doc in docs:
            results.append({
                "title": doc.get("source", "Medical Knowledge Base"),
                "text": doc.get("text", ""),
                "score": doc.get("score", None),
                "source": doc.get("source", ""),
                "category": doc.get("category", "")
            })
        
        logger.info("✓ Direct RAG returned %d documents", len(results))
        return results
    except Exception as e:
        logger.exception("Direct RAG retrieval failed")
        return []
