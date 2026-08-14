# app/services/chat_service.py
import asyncio
from typing import AsyncGenerator

from app.core.llm import llm, llm_lock
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

_SENTINEL = object()


async def stream_chat(
    messages: list[dict],
    temperature: float,
    max_tokens: int,
) -> AsyncGenerator[str, None]:

    loop = asyncio.get_running_loop()
    queue: asyncio.Queue = asyncio.Queue()

    def producer():

        try:
            # Hold the lock for the whole streaming call — no other
            # request (RAG or agent) may touch the shared model while this
            # one is generating. reset() clears any leftover KV-cache state
            # from a previous, unrelated call on this same llm object.
            with llm_lock:
                llm.reset()
                stream = llm.create_chat_completion(
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True,
                )

                for chunk in stream:

                    delta = chunk["choices"][0]["delta"]

                    if "content" in delta:
                        loop.call_soon_threadsafe(
                            queue.put_nowait,
                            delta["content"],
                        )

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
            break

        if isinstance(item, Exception):
            yield "\n\nServer Error"
            return

        yield item