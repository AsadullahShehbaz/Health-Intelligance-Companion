import asyncio

from app.services.rag_chat_service import stream_rag_chat


async def main():
    messages = [
        {
            "role": "user",
            "content": "What are the symptoms of diabetes?"
        }
    ]

    async for token in stream_rag_chat(
        messages=messages,
        temperature=0.7,
        max_tokens=100,
    ):
        print(token, end="", flush=True)


if __name__ == "__main__":
    asyncio.run(main())