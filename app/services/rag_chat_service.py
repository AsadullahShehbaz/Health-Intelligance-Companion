# app/services/rag_chat_service.py

from typing import AsyncGenerator

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.core.llm import llm
from app.core.rag.corrective_rag import corrective_retrieve
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

_ROLE_MAP = {"system": SystemMessage, "user": HumanMessage, "assistant": AIMessage}


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

    user_query = messages[-1]["content"]

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

        rag_messages = messages[:-1] + [{"role": "user", "content": augmented}]
        lc_messages = [_ROLE_MAP[m["role"]](content=m["content"]) for m in rag_messages]

        logger.info("Starting LLM response generation.")

        async for chunk in llm.astream(
            lc_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        ):
            if chunk.content:
                yield chunk.content

    except Exception:
        logger.exception("RAG chat generation failed.")
        yield "\n\nServer Error"