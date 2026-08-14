# app/core/llm.py
from langchain_openai import ChatOpenAI

from app.config import settings
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

logger.info("Initializing LLM client (%s @ %s)", settings.LLM_MODEL, settings.LLM_BASE_URL)

llm = ChatOpenAI(
    base_url=settings.LLM_BASE_URL,
    api_key=settings.LLM_API_KEY,
    model=settings.LLM_MODEL,
    timeout=600
)

logger.info("LLM client ready.")