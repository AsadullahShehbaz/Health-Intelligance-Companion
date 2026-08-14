# app/services/rag_chat_service.py

import asyncio
from typing import AsyncGenerator

from app.core.llm import llm, llm_lock
from app.core.rag.corrective_rag import corrective_retrieve
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

_SENTINEL = object()


def _build_prompt(query: str, docs: list[dict]) -> str:
    context = "\n\n".join(
        f"[{d['source']}] {d['text'][:300]}"
        for d in docs[:3]
    )

    return (
        f"Use the following medical context if relevant.\n\n"
        f"{context}\n\n"
        f"Question: {query}\n"
        f"Answer:"
    )


async def stream_rag_chat(
    messages: list[dict],
    temperature: float,
    max_tokens: int,
) -> AsyncGenerator[str, None]:

    logger.info("Starting RAG chat request.")

    loop = asyncio.get_running_loop()
    queue: asyncio.Queue = asyncio.Queue()

    user_query = messages[-1]["content"]

    def producer():

        try:
            logger.info("Running Corrective RAG retrieval.")

            result = corrective_retrieve(user_query)

            logger.info(
                "Retrieval completed | decision=%s | avg_score=%.3f | docs=%d",
                result["decision"],
                result["avg_score"],
                len(result["docs"]),
            )

            augmented = _build_prompt(
                user_query,
                result["docs"],
            )

            logger.debug("Augmented prompt created.")

            rag_messages = (
                messages[:-1]
                + [{"role": "user", "content": augmented}]
            )

            logger.info("Starting LLM response generation.")

            with llm_lock:
                llm.reset()
                stream = llm.create_chat_completion(
                    messages=rag_messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True,
                )

                token_count = 0

                for chunk in stream:

                    delta = chunk["choices"][0]["delta"]

                    if "content" in delta:
                        token_count += 1

                        loop.call_soon_threadsafe(
                            queue.put_nowait,
                            delta["content"],
                        )

            logger.info(
                "LLM generation completed | streamed_tokens=%d",
                token_count,
            )

        except Exception:
            logger.exception("RAG chat generation failed.")

            loop.call_soon_threadsafe(
                queue.put_nowait,
                Exception(),
            )

        finally:
            logger.debug("Producer finished.")

            loop.call_soon_threadsafe(
                queue.put_nowait,
                _SENTINEL,
            )

    loop.run_in_executor(None, producer)

    while True:

        item = await queue.get()

        if item is _SENTINEL:
            logger.info("Streaming completed.")
            break

        if isinstance(item, Exception):
            logger.error("Streaming terminated due to server error.")
            yield "\n\nServer Error"
            return

        yield item