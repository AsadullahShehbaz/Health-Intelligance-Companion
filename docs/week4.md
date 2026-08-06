Good — since you're running the fine-tuned model locally via `llama-cpp-python`, the earlier plan's HF API call is out; generation should just call your existing `llm` object, and retrieval should follow the same router → service → core pattern you already have for chat. Here's the revised Week 4, day by day.

## Day 1 — Import Kaggle vectors into local Qdrant

You already have the JSON exports. One script, run once:

```python
# scripts/import_vectors.py
import json, glob
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

client = QdrantClient(host="localhost", port=6333)
COLLECTION, EMBED_DIM = "health_knowledge", 384

if client.collection_exists(COLLECTION):
    client.delete_collection(COLLECTION)

client.create_collection(
    collection_name=COLLECTION,
    vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
)

for fpath in sorted(glob.glob("D:/rag_vectors_*.json")):
    chunk = json.load(open(fpath))
    points = [PointStruct(id=i["id"], vector=i["vector"], payload=i["payload"]) for i in chunk]
    for i in range(0, len(points), 100):
        client.upsert(collection_name=COLLECTION, points=points[i:i+100])
    print(f"{fpath}: {len(points)} imported")

print(client.get_collection(COLLECTION).points_count, "total points")
```

Verify at `http://localhost:6333/dashboard`. **Done once — not part of the running app.**

## Day 2 — Embedder + Qdrant retriever (`core/rag/`)

```python
# app/core/rag/embedder.py
from sentence_transformers import SentenceTransformer
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

logger.info("Loading embedding model...")
embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
logger.info("Embedding model loaded.")
```

```python
# app/core/rag/qdrant_store.py
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

from app.core.rag.embedder import embedder
from app.config import settings

client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
COLLECTION = "health_knowledge"


def retrieve(query: str, top_k: int = 5, category: str | None = None) -> list[dict]:
    vector = embedder.encode(query, normalize_embeddings=True).tolist()

    query_filter = None
    if category:
        query_filter = Filter(must=[FieldCondition(key="category", match=MatchValue(value=category))])

    results = client.search(
        collection_name=COLLECTION,
        query_vector=vector,
        query_filter=query_filter,
        limit=top_k,
        with_payload=True,
        score_threshold=0.3,
    )

    return [
        {"text": r.payload.get("text", ""), "source": r.payload.get("source", ""),
         "category": r.payload.get("category", ""), "score": r.score}
        for r in results
    ]
```

Since you already run Qdrant in Docker locally, `settings.QDRANT_URL` can just be `http://localhost:6333` — you don't need the cloud Qdrant vars unless you want to move it later.

**Test this in isolation** — a quick script calling `retrieve("fever and headache")` and printing results — before touching the graph logic.

## Day 3 — Relevance evaluation + correction (the "C" in C-RAG)

```python
# app/core/rag/corrective_rag.py
from app.core.rag.qdrant_store import retrieve
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

RELEVANCE_THRESHOLD = 0.5
AMBIGUOUS_THRESHOLD = 0.35


def evaluate_relevance(docs: list[dict]) -> tuple[str, float]:
    if not docs:
        return "incorrect", 0.0
    scores = [d["score"] for d in docs]
    avg_score, max_score = sum(scores) / len(scores), max(scores)

    if max_score >= RELEVANCE_THRESHOLD:
        return "correct", avg_score
    elif avg_score >= AMBIGUOUS_THRESHOLD:
        return "ambiguous", avg_score
    return "incorrect", avg_score


def web_search_fallback(query: str) -> list[dict]:
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            return [
                {"text": r.get("body", ""), "source": "web_search", "category": "web", "score": 0.5}
                for r in ddgs.text(f"medical {query}", max_results=3)
            ]
    except Exception:
        logger.exception("Web search fallback failed")
        return []


def corrective_retrieve(query: str, top_k: int = 5) -> dict:
    docs = retrieve(query, top_k=top_k)
    decision, avg_score = evaluate_relevance(docs)

    if decision == "incorrect":
        docs = web_search_fallback(query) + docs
    elif decision == "ambiguous":
        docs = docs + web_search_fallback(query)

    return {"docs": docs[:5], "decision": decision, "avg_score": round(avg_score, 3)}
```

Web search is genuinely optional for an FYP demo — if `duckduckgo-search` gives you flaky results behind your network, you can stub `web_search_fallback` to return `[]` and still legitimately claim the corrective *decision* logic as your contribution. Don't let that dependency block Day 3.

**Test**: run `corrective_retrieve()` on a query well inside your dataset (should return `"correct"`) and one clearly outside it, e.g. "who won the world cup" (should trigger `"incorrect"`).

## Day 4 — Wire retrieval into your existing local-LLM streaming pattern

This is the part that changes most from the original plan — no HF API, just reuse `llm` from `core/llm.py` with a RAG-augmented prompt.

```python
# app/services/rag_chat_service.py
import asyncio
from typing import AsyncGenerator

from app.core.llm import llm
from app.core.rag.corrective_rag import corrective_retrieve
from app.utils.logging_config import get_logger

logger = get_logger(__name__)
_SENTINEL = object()


def _build_prompt(query: str, docs: list[dict]) -> str:
    context = "\n\n".join(f"[{d['source']}] {d['text'][:300]}" for d in docs[:3])
    return (
        f"Use the following medical context if relevant.\n\n{context}\n\n"
        f"Question: {query}\nAnswer:"
    )


async def stream_rag_chat(
    messages: list[dict],
    temperature: float,
    max_tokens: int,
) -> AsyncGenerator[str, None]:

    loop = asyncio.get_running_loop()
    queue: asyncio.Queue = asyncio.Queue()

    user_query = messages[-1]["content"]

    def producer():
        try:
            result = corrective_retrieve(user_query)
            augmented = _build_prompt(user_query, result["docs"])

            rag_messages = messages[:-1] + [{"role": "user", "content": augmented}]

            stream = llm.create_chat_completion(
                messages=rag_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )

            for chunk in stream:
                delta = chunk["choices"][0]["delta"]
                if "content" in delta:
                    loop.call_soon_threadsafe(queue.put_nowait, delta["content"])

        except Exception:
            logger.exception("RAG chat generation failed")
            loop.call_soon_threadsafe(queue.put_nowait, Exception())
        finally:
            loop.call_soon_threadsafe(queue.put_nowait, _SENTINEL)

    loop.run_in_executor(None, producer)

    while True:
        item = await queue.get()
        if item is _SENTINEL:
            break
        if isinstance(item, Exception):
            yield "\n\nServer Error"
            return
        yield item
```

This is a near-copy of your `stream_chat` — same threadpool/queue/sentinel pattern — with one addition: `corrective_retrieve()` runs inside the same worker thread before the LLM call, so nothing about your async plumbing changes.

## Day 5 — New route, same shape as `/chat/stream`

```python
# app/api/rag.py
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.schemas.chat import ChatRequest
from app.services.rag_chat_service import stream_rag_chat

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post("/stream")
async def stream(req: ChatRequest):
    messages = [m.model_dump() for m in req.messages]

    return StreamingResponse(
        stream_rag_chat(
            messages=messages,
            temperature=req.temperature,
            max_tokens=req.max_tokens,
        ),
        media_type="text/plain",
    )
```

Register it in `main.py` next to your existing chat router. You reuse `ChatRequest` as-is — no new schema needed yet.

## Updated Week 4 schedule

```
Day 1 → Import Kaggle-generated vectors into local Qdrant (one-off script)
Day 2 → core/rag/embedder.py + qdrant_store.py, test retrieve() in isolation
Day 3 → core/rag/corrective_rag.py — relevance evaluation + optional web fallback
Day 4 → services/rag_chat_service.py — reuse local llm, RAG-augmented prompt
Day 5 → api/rag.py — new /rag/stream endpoint, test in Swagger/Postman
         Compare /chat/stream vs /rag/stream on the same query for your FYP writeup
```

One thing to decide before Day 4: do you want `/rag/stream` to *replace* `/chat/stream` in your UI, or run both side-by-side as a toggle? Side-by-side gives you a much stronger FYP result — a direct before/after comparison of hallucination rate — and it's basically free given how similar the two services already are.