# app/agent/tools.py
from langchain_core.tools import tool

from app.core.rag.rag_tool import perform_direct_rag
from app.core.rag.corrective_rag import web_search_fallback
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


@tool
def retrieve_medical_knowledge(query: str) -> str:
    """Retrieves relevant medical guidelines, clinical notes, or local health docs from the vector database."""
    logger.info("▶ retrieve_medical_knowledge | query=%s", query[:80])
    try:
        docs = perform_direct_rag(query, top_k=5)
        if not docs:
            return "No relevant internal medical documents found."
        logger.info("✓ retrieve_medical_knowledge returned %d docs", len(docs))
        lines = [f"[{d.get('source', 'Medical Knowledge')}]: {d.get('text', '')[:400]}" for d in docs]
        return "Internal Medical Knowledge Results:\n" + "\n\n".join(lines)
    except Exception as e:
        logger.exception("retrieve_medical_knowledge failed")
        return f"Error retrieving knowledge: {e}"


@tool
def search_web_medical(query: str) -> str:
    """Searches the web via SerpAPI for current health information or external guidelines."""
    logger.info("▶ search_web_medical | query=%s", query[:80])
    try:
        results = web_search_fallback(query)
        if not results:
            return "No web search results found."
        lines = [f"[{r.get('title', 'Web Source')}]: {r.get('text', '')}" for r in results[:3]]
        return "Web Search Results:\n" + "\n\n".join(lines)
    except Exception as e:
        logger.exception("search_web_medical failed")
        return f"Error executing web search: {e}"


TOOLS = [
    retrieve_medical_knowledge,
    search_web_medical,
]
