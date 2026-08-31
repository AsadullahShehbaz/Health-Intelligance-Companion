# app/agent/tools.py
import os

import serpapi
from langchain_core.tools import tool
from app.config import settings
from app.core.rag.rag_tool import perform_direct_rag
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

# Initialize SerpAPI client once (reads key from env or settings)
_serp_client = serpapi.Client(api_key=settings.SERP_API_KEY)


@tool(response_format="content_and_artifact")
def retrieve_medical_knowledge(query: str) -> tuple[str, list[dict]]:
    """Retrieves relevant medical guidelines, clinical notes, or local health docs from the vector database."""
    logger.info("▶ retrieve_medical_knowledge | query=%s", query[:80])
    try:
        docs = perform_direct_rag(query, top_k=5)
        if not docs:
            return "No relevant internal medical documents found.", []
        logger.info("✓ retrieve_medical_knowledge returned %d docs", len(docs))
        lines = [
            f"[{d.get('source', 'Medical Knowledge')}]: {d.get('text', '')[:400]}"
            for d in docs
        ]
        content = "Internal Medical Knowledge Results:\n" + "\n\n".join(lines)
        artifact = [{"source": d.get("source", "Medical Knowledge")} for d in docs]
        return content, artifact
    except Exception as e:
        logger.exception("retrieve_medical_knowledge failed")
        return f"Error retrieving knowledge: {e}", []


@tool(response_format="content_and_artifact")
def search_web_medical(query: str) -> tuple[str, list[dict]]:
    """Searches the web via SerpAPI for current health information or external guidelines."""
    logger.info("▶ search_web_medical | query=%s", query[:80])
    try:
        results = _serp_client.search(
            {
                "engine": "google",
                "q": query,
                "hl": "en",
                "gl": "us",
                "num": 5,
            }
        )

        organic = results.get("organic_results", [])
        if not organic:
            return "No web search results found.", []

        lines = []
        artifact = []
        for r in organic[:3]:
            title = r.get("title", "Web Source")
            link = r.get("link", "")
            snippet = r.get("snippet", r.get("description", ""))
            lines.append(f"[{title}]({link}): {snippet}")
            artifact.append({"source": title})

        content = "Web Search Results:\n" + "\n\n".join(lines)
        return content, artifact

    except serpapi.HTTPError as e:
        logger.exception("SerpAPI HTTP error")
        return f"Error executing web search (HTTP {e.status_code}): {e.error}", []
    except Exception as e:
        logger.exception("search_web_medical failed")
        return f"Error executing web search: {e}", []


TOOLS = [
    retrieve_medical_knowledge,
    search_web_medical,
]