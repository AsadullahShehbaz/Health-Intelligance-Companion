# app/services/title_service.py
"""LLM-generated sidebar titles for conversation threads.

The title is produced once, on a thread's first turn (see agent_service.py),
stored in the graph state (``thread_title``), and read back by
conversation_service.py — no separate table; the checkpointer stays the
source of truth for conversation metadata.
"""
import time

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from app.config import settings
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

# Same Groq model as the router/memory LLMs; slightly above-zero temperature
# so titles read naturally, matching the project's LLM-instance conventions.
title_llm = ChatGroq(
    api_key=settings.GROQ_API_KEY,
    model_name=settings.GROQ_MODEL,
    temperature=0.3,
)

DEFAULT_TITLE = "New Conversation"

TITLE_PROMPT = """You are a thread titling assistant for a health companion app.
Summarize the user's initial message into a short, meaningful 3 to 5 word title.

RULES:
- Do NOT use quotes, prefixes (like 'Title:'), or markdown.
- Capitalize key words like a headline.
- If the query is a simple greeting, return 'New Conversation'.
- Keep it clinical yet concise (e.g., 'Persistent Migraine Advice', 'Lab Report Review').
"""

# The sidebar truncates CSS-side, but a chatty model response must never
# become a multi-line mega-title either.
_MAX_TITLE_CHARS = 80


async def generate_thread_title(user_message: str) -> str:
    """Summarize a thread's first user message into a sidebar title.

    Always returns something usable — on empty input or any LLM failure the
    default title is returned (fail-open; a title is cosmetic, never worth
    failing a turn over).
    """
    if not user_message or len(user_message.strip()) < 3:
        return DEFAULT_TITLE

    try:
        start = time.monotonic()
        response = await title_llm.ainvoke([
            SystemMessage(content=TITLE_PROMPT),
            HumanMessage(content=user_message),
        ])
    except Exception:
        logger.exception("Failed to generate thread title — defaulting")
        return DEFAULT_TITLE

    # Post-process: collapse whitespace/newlines, strip wrapping quotes and
    # a possible 'Title:' prefix, cap the length at a word boundary.
    title = " ".join((response.content or "").split())
    title = title.strip("\"'`").strip()
    if title.lower().startswith("title:"):
        title = title[len("title:"):].strip()
    if len(title) > _MAX_TITLE_CHARS:
        title = title[:_MAX_TITLE_CHARS].rsplit(" ", 1)[0]

    logger.info(
        "✓ Generated thread title in %.2fs: %s",
        time.monotonic() - start,
        title,
    )
    return title or DEFAULT_TITLE
