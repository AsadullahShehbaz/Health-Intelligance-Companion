Same pattern as Week 4 — full files, day by day, matching your stack (LangGraph, Pydantic for state/structured output, `LlamaGrammar.from_json_schema` to tie Pydantic directly into constrained decoding on your local GGUF model).

One structural note before the code: **the agent endpoint won't stream token-by-token** like `/chat/stream` and `/rag/stream` do. Multiple nodes (router → rewrite → RAG → reasoner) have to complete before you have a final answer anyway, so streaming mid-graph doesn't give the user anything useful — it'd just be a naked LLM call streaming with a "please wait" in front of it. Real agent frameworks typically return the full response once the graph finishes. This is a deliberate simplification, not a missing feature — flag it in your FYP writeup as a design tradeoff (latency vs. UX) if asked.

## Day 1 — State schema, Pydantic decision model, deterministic nodes

```python
# app/schemas/agent.py
from pydantic import BaseModel, Field
from typing import Optional


class RouterDecision(BaseModel):
    """Structured output contract for the Router Agent. Its JSON schema
    is compiled directly into a llama.cpp grammar, so the model is
    physically constrained to only ever emit this shape."""
    needs_rag: bool = Field(..., description="True if the query needs factual medical lookup")
    save_memory: bool = Field(..., description="True if this message is worth remembering")


class AgentRequest(BaseModel):
    patient_id: str
    query: str
    image_base64: Optional[str] = None


class AgentResponse(BaseModel):
    answer: str
    detected_lang: str
    needs_rag: bool
    retrieval_decision: Optional[str] = None
    sources: list[str] = []
    save_memory: bool
```

```python
# app/agent/state.py
from typing import TypedDict, Optional


class AgentState(TypedDict):
    patient_id: str
    raw_input: str
    has_image: bool
    image_base64: Optional[str]

    detected_lang: str
    english_query: str
    rewritten_query: str

    needs_rag: bool
    save_memory: bool

    retrieved_docs: list[dict]
    retrieval_decision: str

    recent_memory: list[dict]

    answer: str
    final_response: str
```

```python
# app/core/rag/ocr.py
import base64
import io
from PIL import Image
import pytesseract

from app.utils.logging_config import get_logger

logger = get_logger(__name__)


def extract_text_from_base64(image_b64: str) -> str:
    try:
        image_bytes = base64.b64decode(image_b64)
        image = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception:
        logger.exception("OCR extraction failed")
        return ""
```

```python
# app/core/rag/translation.py
from deep_translator import GoogleTranslator
from langdetect import detect, LangDetectException

from app.utils.logging_config import get_logger

logger = get_logger(__name__)


def detect_language(text: str) -> str:
    try:
        return detect(text)
    except LangDetectException:
        return "en"


def to_english(text: str, source_lang: str) -> str:
    if source_lang == "en":
        return text
    try:
        return GoogleTranslator(source="auto", target="english").translate(text)
    except Exception:
        logger.exception("Translation to English failed, falling back to original text")
        return text


def from_english(text: str, target_lang: str) -> str:
    if target_lang == "en":
        return text
    try:
        return GoogleTranslator(source="english", target=target_lang).translate(text)
    except Exception:
        logger.exception("Translation back to source language failed, returning English")
        return text
```

```python
# app/models/memory.py
from sqlalchemy import Column, String, Text, DateTime, func
from app.db.base import Base


class ConversationMemory(Base):
    __tablename__ = "conversation_memory"

    id = Column(String, primary_key=True, default=lambda: __import__("uuid").uuid4().hex)
    patient_id = Column(String, index=True, nullable=False)
    query = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

```python
# app/core/rag/memory_store.py
"""
Sync engine, separate from the app's async SQLAlchemy engine. Memory
node functions run inside a worker thread (via run_in_threadpool), not
inside the event loop, so a plain sync session is simpler and safer
here than juggling async calls from a sync context.
"""
from sqlalchemy import create_engine, select, desc
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.memory import ConversationMemory
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

sync_url = settings.DATABASE_URL.replace("postgresql+asyncpg", "postgresql")
engine = create_engine(sync_url)
SyncSession = sessionmaker(bind=engine)


def get_recent_memory(patient_id: str, limit: int = 3) -> list[dict]:
    try:
        with SyncSession() as session:
            rows = session.execute(
                select(ConversationMemory)
                .where(ConversationMemory.patient_id == patient_id)
                .order_by(desc(ConversationMemory.created_at))
                .limit(limit)
            ).scalars().all()
            return [{"query": r.query, "answer": r.answer} for r in reversed(rows)]
    except Exception:
        logger.exception("Failed to fetch recent memory")
        return []


def save_memory(patient_id: str, query: str, answer: str) -> None:
    try:
        with SyncSession() as session:
            session.add(ConversationMemory(patient_id=patient_id, query=query, answer=answer))
            session.commit()
    except Exception:
        logger.exception("Failed to save memory")
```

```python
# app/agent/nodes/ocr_node.py
from app.agent.state import AgentState
from app.core.rag.ocr import extract_text_from_base64


def ocr_node(state: AgentState) -> AgentState:
    if not state.get("has_image"):
        return state
    extracted = extract_text_from_base64(state["image_base64"])
    if extracted:
        state["raw_input"] = f"{state['raw_input']}\n{extracted}".strip()
    return state
```

```python
# app/agent/nodes/translate_node.py
from app.agent.state import AgentState
from app.core.rag.translation import detect_language, to_english, from_english


def translate_in_node(state: AgentState) -> AgentState:
    lang = detect_language(state["raw_input"])
    state["detected_lang"] = lang
    state["english_query"] = to_english(state["raw_input"], lang)
    return state


def translate_out_node(state: AgentState) -> AgentState:
    if state["detected_lang"] == "en":
        state["final_response"] = state["answer"]
    else:
        state["final_response"] = from_english(state["answer"], state["detected_lang"])
    return state
```

```python
# app/agent/nodes/memory_node.py
from app.agent.state import AgentState
from app.core.rag.memory_store import get_recent_memory, save_memory


def get_memory_node(state: AgentState) -> AgentState:
    state["recent_memory"] = get_recent_memory(state["patient_id"], limit=3)
    return state


def save_memory_node(state: AgentState) -> AgentState:
    if state.get("save_memory"):
        save_memory(state["patient_id"], state["english_query"], state["answer"])
    return state
```

**Test each node in isolation** before Day 2 — e.g. call `ocr_node({"has_image": True, "image_base64": ..., "raw_input": ""})` directly and check the output dict.

## Day 2 — Router Agent (Pydantic → grammar → structured output)

```python
# app/agent/nodes/router_node.py
import json
from llama_cpp import LlamaGrammar

from app.core.llm import llm
from app.agent.state import AgentState
from app.schemas.agent import RouterDecision
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

# Compile the Pydantic model's JSON schema directly into a llama.cpp
# grammar. This is the actual link between "Pydantic" and "Structured
# Output" in your stack — the model is physically unable to emit
# anything that doesn't validate against RouterDecision.
_SCHEMA = RouterDecision.model_json_schema()
_GRAMMAR = LlamaGrammar.from_json_schema(json.dumps(_SCHEMA))

ROUTER_PROMPT = """You are a routing assistant for a medical Q&A system.
Given the user's message, decide:
- needs_rag: true if this is a medical question needing factual lookup, false for greetings/small talk/non-medical chat
- save_memory: true if this message contains meaningful health info worth remembering, false for small talk

Examples:
User: "hello, how are you"
{{"needs_rag": false, "save_memory": false}}

User: "I have had a fever and body pain for two days"
{{"needs_rag": true, "save_memory": true}}

User: "what's the weather like today"
{{"needs_rag": false, "save_memory": false}}

User: "I feel dizzy"
{{"needs_rag": true, "save_memory": true}}

User: "is this the same headache as last time"
{{"needs_rag": true, "save_memory": true}}

User: "thank you, that helps"
{{"needs_rag": false, "save_memory": false}}

Now classify this message:
User: "{query}"
Respond with ONLY the JSON object."""


def router_node(state: AgentState) -> AgentState:
    output = llm(
        ROUTER_PROMPT.format(query=state["english_query"]),
        grammar=_GRAMMAR,
        max_tokens=50,
        temperature=0.1,
    )
    raw = output["choices"][0]["text"]

    try:
        decision = RouterDecision.model_validate_json(raw)
    except Exception:
        logger.exception(f"Router output failed validation: {raw!r} — defaulting to safe fallback")
        decision = RouterDecision(needs_rag=True, save_memory=True)  # fail safe, not silent

    state["needs_rag"] = decision.needs_rag
    state["save_memory"] = decision.save_memory
    return state
```

The fallback matters: if the grammar-constrained call ever produces something `RouterDecision` can't parse (rare, but possible with edge-case Unicode or truncation), default to `needs_rag=True` — a wasted RAG lookup is a much cheaper mistake than silently skipping retrieval on a real medical question.

**Manually test 20-30 varied inputs here** — this is your single point of failure for the whole graph, worth real time.

## Day 3 — Query Rewriter Agent + RAG node

```python
# app/agent/nodes/rewriter_node.py
from app.core.llm import llm
from app.agent.state import AgentState

REWRITER_PROMPT = """Rewrite the user's message into a clear, specific
medical question suitable for a search query. Keep it short — one
sentence. If the message is already clear, return it unchanged.

Recent conversation:
{memory}

User message: "{query}"

Rewritten query:"""


def _format_memory(memory: list[dict]) -> str:
    if not memory:
        return "(no prior context)"
    return "\n".join(f"Q: {m['query']}\nA: {m['answer'][:150]}" for m in memory)


def query_rewriter_node(state: AgentState) -> AgentState:
    prompt = REWRITER_PROMPT.format(
        memory=_format_memory(state.get("recent_memory", [])),
        query=state["english_query"],
    )
    output = llm(prompt, max_tokens=80, temperature=0.3)
    rewritten = output["choices"][0]["text"].strip()
    state["rewritten_query"] = rewritten if rewritten else state["english_query"]
    return state
```

```python
# app/agent/nodes/rag_node.py
from app.agent.state import AgentState
from app.core.rag.corrective_rag import corrective_retrieve


def rag_node(state: AgentState) -> AgentState:
    query = state.get("rewritten_query") or state["english_query"]
    result = corrective_retrieve(query)
    state["retrieved_docs"] = result["docs"]
    state["retrieval_decision"] = result["decision"]
    return state
```

Reuses your existing Week 4 `corrective_retrieve` untouched — no changes needed there.

## Day 4 — Medical Reasoner Agent + graph assembly

```python
# app/agent/nodes/reasoner_node.py
from app.core.llm import llm
from app.agent.state import AgentState


def _format_context(docs: list[dict]) -> str:
    if not docs:
        return ""
    return "\n\n".join(f"[{d['source']}] {d['text'][:300]}" for d in docs[:3])


def _format_memory(memory: list[dict]) -> str:
    if not memory:
        return ""
    return "\n".join(f"Patient previously asked: {m['query']}\nYou answered: {m['answer'][:150]}" for m in memory)


def reasoner_node(state: AgentState) -> AgentState:
    query = state.get("rewritten_query") or state["english_query"]

    parts = []
    memory_block = _format_memory(state.get("recent_memory", []))
    if memory_block:
        parts.append(f"Conversation history:\n{memory_block}")

    if state.get("needs_rag"):
        context_block = _format_context(state.get("retrieved_docs", []))
        if context_block:
            parts.append(f"Relevant medical context:\n{context_block}")

    parts.append(f"Question: {query}\nAnswer:")
    prompt = "\n\n".join(parts)

    response = llm.create_chat_completion(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=400,
        stream=False,
    )
    state["answer"] = response["choices"][0]["message"]["content"].strip()
    return state
```

```python
# app/agent/graph.py
from langgraph.graph import StateGraph, END

from app.agent.state import AgentState
from app.agent.nodes.ocr_node import ocr_node
from app.agent.nodes.translate_node import translate_in_node, translate_out_node
from app.agent.nodes.router_node import router_node
from app.agent.nodes.memory_node import get_memory_node, save_memory_node
from app.agent.nodes.rewriter_node import query_rewriter_node
from app.agent.nodes.rag_node import rag_node
from app.agent.nodes.reasoner_node import reasoner_node


def _route_after_router(state: AgentState) -> str:
    return "rewrite" if state["needs_rag"] else "reasoner"


def build_health_agent():
    graph = StateGraph(AgentState)

    graph.add_node("ocr", ocr_node)
    graph.add_node("translate_in", translate_in_node)
    graph.add_node("router", router_node)
    graph.add_node("get_memory", get_memory_node)
    graph.add_node("rewrite", query_rewriter_node)
    graph.add_node("rag", rag_node)
    graph.add_node("reasoner", reasoner_node)
    graph.add_node("save_memory", save_memory_node)
    graph.add_node("translate_out", translate_out_node)

    graph.set_entry_point("ocr")
    graph.add_edge("ocr", "translate_in")
    graph.add_edge("translate_in", "router")
    graph.add_edge("router", "get_memory")
    graph.add_conditional_edges(
        "get_memory", _route_after_router, {"rewrite": "rewrite", "reasoner": "reasoner"}
    )
    graph.add_edge("rewrite", "rag")
    graph.add_edge("rag", "reasoner")
    graph.add_edge("reasoner", "save_memory")
    graph.add_edge("save_memory", "translate_out")
    graph.add_edge("translate_out", END)

    return graph.compile()
```

**Full end-to-end test**: 5-10 real conversations through `agent.invoke(initial_state)` directly in a script, checking each state field populates as expected, before wiring the API route.

## Day 5 — Service layer + FastAPI route

```python
# app/services/agent_service.py
from starlette.concurrency import run_in_threadpool

from app.agent.graph import build_health_agent
from app.schemas.agent import AgentRequest, AgentResponse
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

# Compiled once at import time — reused across requests, same pattern
# as loading `llm` once in core/llm.py
agent = build_health_agent()


def _build_initial_state(req: AgentRequest) -> dict:
    return {
        "patient_id": req.patient_id,
        "raw_input": req.query,
        "has_image": req.image_base64 is not None,
        "image_base64": req.image_base64,
        "detected_lang": "",
        "english_query": "",
        "rewritten_query": "",
        "needs_rag": False,
        "save_memory": False,
        "retrieved_docs": [],
        "retrieval_decision": "",
        "recent_memory": [],
        "answer": "",
        "final_response": "",
    }


async def run_agent(req: AgentRequest) -> AgentResponse:
    initial_state = _build_initial_state(req)

    try:
        result = await run_in_threadpool(agent.invoke, initial_state)
    except Exception:
        logger.exception("Agent graph execution failed")
        raise

    return AgentResponse(
        answer=result["final_response"],
        detected_lang=result["detected_lang"],
        needs_rag=result["needs_rag"],
        retrieval_decision=result.get("retrieval_decision") or None,
        sources=[d["source"] for d in result.get("retrieved_docs", [])[:3]],
        save_memory=result["save_memory"],
    )
```

```python
# app/api/agent.py
from fastapi import APIRouter, HTTPException

from app.schemas.agent import AgentRequest, AgentResponse
from app.services.agent_service import run_agent

router = APIRouter(prefix="/agent", tags=["Agent"])


@router.post("/invoke", response_model=AgentResponse)
async def invoke(req: AgentRequest):
    try:
        return await run_agent(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

```python
# app/main.py — add alongside your existing routers
from app.api import auth, chat, rag, agent  # add `agent`

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(rag.router)
app.include_router(agent.router)   # new
```

## Week 5 schedule

```
Day 1 → State + Pydantic schemas, OCR/translation/memory core modules,
         all deterministic nodes — test each in isolation
Day 2 → Router agent with Pydantic-compiled grammar + few-shot prompt
         Manual test on 20-30 varied inputs
Day 3 → Query Rewriter agent + rag_node (reuses Week 4 CRAG untouched)
Day 4 → Medical Reasoner agent + graph.py assembly
         5-10 end-to-end test conversations via agent.invoke()
Day 5 → agent_service.py + api/agent.py + register in main.py
         Compare /agent/invoke vs /rag/stream vs /chat/stream on your
         test set — three-way comparison strengthens the FYP evaluation
```

One thing to decide before Day 1: `pytesseract` needs the Tesseract binary installed system-wide (not just `pip install`), separate from your Python deps — worth confirming it's on your machine before Day 1 rather than discovering it mid-week.