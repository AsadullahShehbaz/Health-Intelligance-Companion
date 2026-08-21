# app/core/llm.py
import httpx
from langchain_openai import ChatOpenAI

from app.config import settings
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


def validate_llm_connection() -> None:
    """Check that the configured OpenAI-compatible model server is reachable.

    The app may start successfully even when the assistant backend is down, so we
    fail with a clear, actionable error instead of exposing a raw socket error to
    the API client.
    """
    if not settings.LLM_BASE_URL:
        raise RuntimeError(
            "LLM backend is not configured. Set LLM_BASE_URL in your environment or .env file."
        )

    try:
        response = httpx.get(settings.LLM_BASE_URL, timeout=5)
    except httpx.HTTPError as exc:
        raise RuntimeError(
            "LLM backend is unreachable at "
            f"{settings.LLM_BASE_URL}. Start the local llama-server or set the correct "
            "LLM_BASE_URL / LLM_API_KEY in .env."
        ) from exc

    if response.status_code not in {200, 404, 405}:
        raise RuntimeError(
            "LLM backend responded with an error at "
            f"{settings.LLM_BASE_URL} (HTTP {response.status_code}). "
            "Check that the model server is running and the LLM configuration is correct."
        )


logger.info("Initializing LLM client (%s @ %s)", settings.LLM_MODEL, settings.LLM_BASE_URL)

llm = ChatOpenAI(
    base_url=settings.LLM_BASE_URL,
    api_key=settings.LLM_API_KEY,
    model=settings.LLM_MODEL,
    timeout=600,
    max_retries=0,
)

logger.info("LLM client ready.")