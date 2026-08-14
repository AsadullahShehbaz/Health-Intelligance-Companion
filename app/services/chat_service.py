# app/services/chat_service.py
from typing import AsyncGenerator

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.core.llm import llm
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

_ROLE_MAP = {"system": SystemMessage, "user": HumanMessage, "assistant": AIMessage}


async def stream_chat(
    messages: list[dict],
    temperature: float,
    max_tokens: int,
) -> AsyncGenerator[str, None]:
    lc_messages = [_ROLE_MAP[m["role"]](content=m["content"]) for m in messages]

    logger.info(
        "▶ stream_chat started | messages=%d | temperature=%.2f | max_tokens=%d",
        len(lc_messages),
        temperature,
        max_tokens,
    )
    try:
        async for chunk in llm.astream(
            lc_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        ):
            if chunk.content:
                yield chunk.content
        logger.info("✓ stream_chat completed")
    except Exception:
        logger.exception("Chat generation failed")
        yield "\n\nServer Error"