# app/services/chat_service.py
import asyncio
from typing import AsyncGenerator

from app.core.llm import llm
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

_SENTINEL = object()


async def stream_chat(
    messages: list[dict],
    temperature: float,
    max_tokens: int,
) -> AsyncGenerator[str, None]:
    logger.debug(
        "Starting stream_chat | msg_count=%d, temp=%.2f, max_tokens=%d",
        len(messages),
        temperature,
        max_tokens,
    )
    logger.info(f"Message : {messages}")
    loop = asyncio.get_running_loop()
    queue: asyncio.Queue = asyncio.Queue()

    def producer():
        chunk_count = 0
        try:
            logger.debug("Initializing LLM completion stream...")
            stream = llm.create_chat_completion(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )

            for chunk in stream:
                delta = chunk["choices"][0]["delta"]

                if "content" in delta:
                    chunk_count += 1
                    loop.call_soon_threadsafe(
                        queue.put_nowait,
                        delta["content"],
                    )

            logger.debug("Producer finished. Total chunks yielded: %d", chunk_count)

        except Exception:
            logger.exception("Chat generation failed")

            loop.call_soon_threadsafe(
                queue.put_nowait,
                Exception(),
            )

        finally:
            loop.call_soon_threadsafe(
                queue.put_nowait,
                _SENTINEL,
            )

    loop.run_in_executor(None, producer)

    while True:
        item = await queue.get()

        if item is _SENTINEL:
            logger.debug("stream_chat completed successfully")
            break

        if isinstance(item, Exception):
            logger.debug("stream_chat terminating due to error")
            yield "\n\nServer Error"
            return

        yield item