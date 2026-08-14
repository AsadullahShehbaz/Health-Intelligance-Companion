# Migrating `agent_node.py` from llama.cpp Grammar → LangChain `bind_tools()`

**Goal:** Replace the local `llama-cpp-python` + `LlamaGrammar.from_json_schema()` JSON-forcing
hack with real OpenAI-style tool calling via `langchain-openai`'s `ChatOpenAI`, pointed at your
OpenAI-compatible endpoint (llama.app or a self-hosted `llama-server --api` / vLLM / etc).

---

## 1. Why this is a net simplification

| Concern | Today (llama.cpp + grammar) | After (`ChatOpenAI.bind_tools`) |
|---|---|---|
| Forcing valid JSON output | `LlamaGrammar.from_json_schema(ToolCall schema)` | Not needed — the server enforces the tool-call wire format |
| Deciding action vs. answer | Custom `ToolCall.action: Literal[...]` field incl. a fake `"final_answer"` action | Native: `AIMessage.tool_calls` empty → it's a final answer. `tools_condition` already checks this. |
| Building the `AIMessage` with `tool_calls=[...]` | Hand-built dict `{"id": ..., "name": ..., "args": ...}` | Returned directly by the model, already LangChain-shaped |
| Blank/garbled answer recovery (`_plain_answer_fallback`, `MIN_USABLE_ANSWER_CHARS`) | Needed because small local models under grammar constraints sometimes emit empty `answer` | Mostly unnecessary — proper tool-calling models return real content or a genuine tool call, not malformed JSON |
| Thread-blocking model calls (`llm_lock`, `run_in_executor`) | Needed because `llama_cpp` is synchronous and stateful (KV cache) | Not needed — `ChatOpenAI` is an async HTTP client, safe for concurrent calls |
| Tool docs baked into a giant prompt string (`_TOOL_DOCS`) | Manual, has to be kept in sync with `tools.py` | Not needed — tool `name`/`description`/`args_schema` come from the `@tool` decorator you already have |

Net effect: `agent_node.py` shrinks from ~180 lines to ~70, and two whole failure-recovery code
paths disappear because they existed specifically to work around grammar-constrained small-model
quirks.

---

## 2. Dependency changes — `requirements.txt`

Remove:
```
gguf==0.19.0
llama_cpp_python==0.3.34
```

Add:
```
langchain-openai>=0.3.0
```

You already have `langchain-core` and `langgraph`, those stay as-is.

```bash
conda activate ft-project
pip uninstall llama_cpp_python gguf -y
pip install langchain-openai
```

---

## 3. Config — `app/config.py`

Replace `MODEL_PATH` with connection settings for your OpenAI-compatible endpoint.

```python
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── Database ──────────────────────────────────────────────────────────
    DATABASE_URL: str
    QDRANT_URL: str
    QDRANT_API_KEY: str

    # ── Auth ──────────────────────────────────────────────────────────────
    HF_TOKEN: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    RESET_TOKEN_EXPIRE_HOURS: int = 1
    VERIFY_TOKEN_EXPIRE_HOURS: int = 48

    # ── LLM (OpenAI-compatible endpoint, e.g. llama.app) ───────────────────
    LLM_BASE_URL: str = "https://api.llama.app/v1"   # or your self-hosted server URL
    LLM_API_KEY: str                                  # required even for local servers that ignore it
    LLM_MODEL: str = "your-model-name"                # whatever the server expects in `model`
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 900

    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    # ── Email / SMTP ────────────────────────────────────────────────────────
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""
    SMTP_TLS: bool = True

    SERP_API_KEY: str
    GROQ_API_KEY: str
    model_config = ConfigDict(env_file=".env", extra="ignore")


settings = Settings()
```

Add to `.env`:
```
LLM_BASE_URL=https://api.llama.app/v1
LLM_API_KEY=sk-...
LLM_MODEL=llama-3.1-70b-instruct   # example — use whatever your endpoint exposes
```

Update `app/main.py`'s `validate_settings()` to check `LLM_API_KEY` instead of implicitly
depending on `MODEL_PATH` existing on disk:

```python
def validate_settings():
    required = [
        settings.DATABASE_URL,
        settings.SECRET_KEY,
        settings.QDRANT_URL,
        settings.GROQ_API_KEY,
        settings.LLM_API_KEY,
    ]
    if not all(required):
        raise RuntimeError("Missing required environment variables")
```

---

## 4. LLM client — `app/core/llm.py`

This is the biggest conceptual change: from a module-level `Llama` object + a global lock, to a
module-level `ChatOpenAI` client (stateless, thread/async-safe, no lock needed).

```python
# app/core/llm.py
from langchain_openai import ChatOpenAI

from app.config import settings
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

logger.info("Initializing LLM client (%s @ %s)", settings.LLM_MODEL, settings.LLM_BASE_URL)

# A single shared client is fine here: ChatOpenAI wraps an async-capable HTTP
# client under the hood, so — unlike the old llama_cpp.Llama object — there is
# no shared mutable state (KV cache) between calls and no lock is required.
# Each .invoke()/.ainvoke()/.astream() call is independent.
llm = ChatOpenAI(
    base_url=settings.LLM_BASE_URL,
    api_key=settings.LLM_API_KEY,
    model=settings.LLM_MODEL,
    temperature=settings.LLM_TEMPERATURE,
    max_tokens=settings.LLM_MAX_TOKENS,
    timeout=60,
    max_retries=2,
)

logger.info("LLM client ready.")
```

Delete:
- `llm_lock`
- `n_ctx`, `n_threads`, `n_batch` tuning (server-side concern now, not yours)
- the long comment about KV-cache contention between `chat_service`/`rag_chat_service`/`agent_node`
  sharing one `Llama` object — that whole problem class is gone.

---

## 5. Tools — `app/agent/tools.py`

**No changes required.** You're already using `langchain_core.tools.tool`, which is exactly what
`bind_tools()` consumes. `fetch_patient_facts`, `retrieve_medical_knowledge`, `save_patient_fact`,
`save_emotional_state`, and the `TOOLS` list all work unmodified.

---

## 6. Schema — `app/schemas/agent.py`

Delete the grammar-only `ToolCall` model entirely:

```python
# DELETE THIS — no longer needed, bind_tools() handles structured tool calls natively
class ToolCall(BaseModel):
    thought: str = Field(...)
    action: Literal[...]
    action_input: dict = Field(default_factory=dict)
    answer: str = Field(default="", description=...)
```

Keep `AgentRequest`, `AgentResponse`, `ConversationMessage`, `ConversationMeta`,
`ConversationDetail` — unrelated to the LLM call format.

---

## 7. Prompt — `app/agent/prompt.py`

You can delete `SYSTEM_PROMPT` from `prompt.py` (it was designed around manually-listed tool docs
and the fake `final_answer` action) and replace it with a much shorter system prompt that doesn't
need to describe tools at all — the model sees real tool schemas via `bind_tools()`.

```python
# app/agent/prompt.py
SYSTEM_PROMPT = """You are an empathetic Pakistani AI health companion.

RULES:
- If the patient's message is a greeting, small talk, thanks, a personal question
  (e.g. "what is my name"), or anything that is not a medical symptom or health
  question, answer directly in plain text. Do NOT call any tools, and do NOT use
  the Diagnosis/Medicines format for these.
- Only use fetch_patient_facts / retrieve_medical_knowledge when the patient
  describes an actual symptom or asks a medical question.
- Never call the same tool with the same input more than once in a turn. Check the
  conversation so far before choosing an action.
- Only use tools when they would materially improve your answer. If you already
  have enough information, answer directly.
- For a real MEDICAL concern, format your final answer as:
  **Diagnosis:** ...
  **Confidence:** ...
  **Medicines:** ...
  **Diet:** ...
  **Exercise:** ...
  **When to see a doctor:** ...
- For anything else (greetings, personal questions, general requests), reply
  normally in plain text.
- For potentially serious symptoms, clearly recommend seeking professional
  medical care.
- Never invent patient history, medical facts, or tool results.

Patient ID: {patient_id}
"""
```

---

## 8. The main rewrite — `app/agent/nodes/agent_node.py`

This is the file that actually changes shape. Old flow: build one big prompt string → call
`llm(prompt, grammar=_GRAMMAR)` → parse JSON → branch on `.action` → hand-build an `AIMessage`.

New flow: build a proper LangChain message list → call `bound_llm.invoke(messages)` → the
returned `AIMessage` already has `.content` and `.tool_calls` populated correctly.

```python
# app/agent/nodes/agent_node.py
import re

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.core.llm import llm
from app.agent.state import AgentState
from app.agent.prompt import SYSTEM_PROMPT
from app.agent.tools import TOOLS
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

MAX_TOOL_CALLS = 4

# Bound once at import time — cheap, and avoids re-binding schemas on every call.
_llm_with_tools = llm.bind_tools(TOOLS)


def _document_section(state: AgentState) -> str:
    text = state.get("ocr_context", "")
    if not text:
        return ""
    return (
        "Attached document (from the patient's photo):\n"
        f"{text[:1000]}\n\n"
        "The patient attached this medical document and wants it explained, "
        "verified, or advised on — answer questions about it directly."
    )


def agent_node(state: AgentState) -> AgentState:
    count = state.get("tool_call_count", 0)
    forced_final = count >= MAX_TOOL_CALLS

    system_text = SYSTEM_PROMPT.format(patient_id=state["patient_id"])
    doc_section = _document_section(state)
    if doc_section:
        system_text = doc_section + "\n\n" + system_text

    # Build the message list for THIS call. `state["messages"]` already accumulates
    # AIMessage/ToolMessage pairs across the tool loop via the add_messages reducer
    # in AgentState, so we only need to seed it with the system prompt and (on the
    # very first turn of the loop) the human query.
    prior = state.get("messages", [])
    has_human_turn = any(isinstance(m, HumanMessage) for m in prior)
    messages = [SystemMessage(content=system_text), *prior]
    if not has_human_turn:
        messages.append(HumanMessage(content=state["raw_input"]))

    # On the forced-final pass, drop tool binding entirely so the model MUST
    # answer in plain text instead of attempting another tool call.
    model = llm if forced_final else _llm_with_tools
    response: AIMessage = model.invoke(messages)

    if forced_final and response.tool_calls:
        # Extremely rare with an OpenAI-compatible model, but stay defensive:
        # strip any tool_calls the model tried to sneak in on the forced pass.
        response = AIMessage(content=response.content or "Let me summarize what I know so far.")

    if response.tool_calls:
        state["tool_call_count"] = count + 1
    else:
        answer_text = (response.content or "").strip()
        if not answer_text:
            answer_text = (
                "I'm sorry, I wasn't able to generate a proper response to that. "
                "Could you try rephrasing your message?"
            )
            response = AIMessage(content=answer_text)
        state["answer"] = answer_text
        state["final_response"] = answer_text

    # ── Same post-hoc bookkeeping as before: scan ToolMessages produced by
    #    ToolNode to populate needs_rag / retrieval_decision / retrieved_docs /
    #    saved_memory for the sidebar + AgentResponse. Unchanged logic. ──
    tool_msgs = [m for m in state.get("messages", []) if getattr(m, "type", None) == "tool"]
    rag_used = any(getattr(m, "name", "") == "retrieve_medical_knowledge" for m in tool_msgs)
    state["needs_rag"] = rag_used

    decision_text = ""
    sources: list[str] = []
    for m in tool_msgs:
        if getattr(m, "name", "") != "retrieve_medical_knowledge":
            continue
        for line in (m.content or "").splitlines():
            if "Retrieval decision" in line:
                match = re.search(r"Retrieval decision:\s*([A-Za-z]+)", line)
                if match:
                    decision_text = match.group(1)
            else:
                match = re.match(r"^\s*\[([^\]]+)\]", line)
                if match:
                    sources.append(match.group(1))
    state["retrieval_decision"] = decision_text or ("retrieved" if rag_used else "")
    state["retrieved_docs"] = [{"source": s} for s in sources[:3]]
    state["saved_memory"] = any(
        getattr(m, "name", "") in ("save_patient_fact", "save_emotional_state") for m in tool_msgs
    )

    state["messages"] = [response]
    return state
```

### What got deleted, and why it's safe to delete

- `_SCHEMA` / `_GRAMMAR` / `LlamaGrammar.from_json_schema` — the server now enforces valid
  tool-call structure; nothing to constrain client-side.
- `_TOOL_DOCS` string — tool descriptions now come from each `@tool`-decorated function's
  docstring, exactly as `ToolNode` already uses them.
- `ToolCall.model_validate_json(raw)` / the `except Exception` fallback path — you're no longer
  parsing free-form text as JSON, so there's no malformed-JSON failure mode to catch.
- `_plain_answer_fallback()` — this existed specifically because grammar-constrained small models
  sometimes returned a blank `answer` field. A well-behaved OpenAI-compatible endpoint returns
  real content directly on `response.content`. The lightweight blank-string guard above is kept
  purely as a defensive fallback, not a required recovery path.
- `MIN_USABLE_ANSWER_CHARS` heuristic — same reasoning, kept only as a minimal safety net.

---

## 9. Graph — `app/agent/graph.py`

**No structural changes needed.** `ToolNode(TOOLS)`, `tools_condition`, `_route_after_agent`, and
`build_health_agent()` all operate on `AIMessage.tool_calls`, which is exactly the shape
`bind_tools()` produces — this is the same contract `ToolNode` already expected from your manually
built `AIMessage` before.

One optional cleanup: since `agent_node` is no longer synchronous-and-blocking-on-a-local-model,
you *could* eventually make the whole graph async (`ainvoke` throughout,
`run_in_threadpool` → `await agent.ainvoke(...)` directly) for better throughput. Not required for
this migration — leaving `agent_service.py`'s `run_in_threadpool(agent.invoke, ...)` pattern as-is
still works fine and is a smaller diff.

---

## 10. Streaming — `app/services/chat_service.py` & `app/services/rag_chat_service.py`

These currently exist mainly to bridge `llama_cpp`'s **synchronous** streaming generator onto
asyncio via a thread executor + `asyncio.Queue`. `ChatOpenAI` supports native async streaming, so
this entire bridge collapses to a plain `async for` loop.

**`app/services/chat_service.py`:**

```python
# app/services/chat_service.py
from typing import AsyncGenerator

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

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

    try:
        async for chunk in llm.astream(
            lc_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        ):
            if chunk.content:
                yield chunk.content
    except Exception:
        logger.exception("Chat generation failed")
        yield "\n\nServer Error"
```

**`app/services/rag_chat_service.py`:** same idea — keep `corrective_retrieve()` and
`_build_prompt()` exactly as they are (they're retrieval logic, not LLM-format logic), just swap
the generation step:

```python
# app/services/rag_chat_service.py
from typing import AsyncGenerator

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from app.core.llm import llm
from app.core.rag.corrective_rag import corrective_retrieve
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

_ROLE_MAP = {"system": SystemMessage, "user": HumanMessage, "assistant": AIMessage}


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
    logger.info("Starting RAG chat request.")
    user_query = messages[-1]["content"]

    try:
        result = corrective_retrieve(user_query)
        logger.info(
            "Retrieval completed | decision=%s | avg_score=%.3f | docs=%d",
            result["decision"], result["avg_score"], len(result["docs"]),
        )

        augmented = _build_prompt(user_query, result["docs"])
        rag_messages = messages[:-1] + [{"role": "user", "content": augmented}]
        lc_messages = [_ROLE_MAP[m["role"]](content=m["content"]) for m in rag_messages]

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
```

Delete from both files: `asyncio.Queue`, `_SENTINEL`, `loop.run_in_executor`,
`loop.call_soon_threadsafe`, `llm.reset()`, `llm_lock` — none of it is needed once the model call
itself is natively async.

The `/chat/stream` and `/rag/stream` FastAPI routes in `app/api/chat.py` / `app/api/rag.py`
**don't need to change** — they already just wrap the generator in `StreamingResponse`.

---

## 11. `app/services/agent_service.py`

No changes required. It calls `run_agent()` → `run_in_threadpool(agent.invoke, state, config)`,
which is unaffected — the graph's node signature (`state -> state`) didn't change, just what
happens *inside* `agent_node`.

---

## 12. Migration checklist (do it in this order)

1. Add `LLM_BASE_URL` / `LLM_API_KEY` / `LLM_MODEL` to `.env` and `Settings`.
2. `pip install langchain-openai && pip uninstall llama_cpp_python gguf`.
3. Rewrite `app/core/llm.py` (Section 4).
4. Simplify `app/agent/prompt.py` (Section 7).
5. Rewrite `app/agent/nodes/agent_node.py` (Section 8) — this is where the actual grammar→tools
   swap happens.
6. Delete `ToolCall` from `app/schemas/agent.py` (Section 6).
7. Rewrite `app/services/chat_service.py` and `app/services/rag_chat_service.py` (Section 10).
8. Leave `app/agent/tools.py`, `app/agent/graph.py`, `app/services/agent_service.py`,
   `app/agent/state.py`, and `app/db/*` completely untouched.
9. Run your existing smoke tests against a live backend:
   ```bash
   conda activate ft-project
   python app/tests/test_week6_agent.py 4      # hello → symptom → memory recall → emotion
   python app/tests/test-ocr.py                # OCR + agent flow
   python app/tests/test_chat.py               # plain /chat/stream
   ```
   These already exercise exactly the code paths that changed (tool-calling loop, memory
   recall, OCR-aware answering, streaming), so they're your regression suite for this migration —
   no new test files needed.

## 13. One correctness gotcha to watch for

Your current `agent_node.py` never actually appends a `HumanMessage` for the user's query into
`state["messages"]` — it only ever appends the `AIMessage` decisions. That worked under the old
grammar approach because everything (system rules + query + prior tool results) was flattened into
one prompt string per call anyway. Step 8's rewrite fixes this by adding a `HumanMessage` on the
first pass through the tool loop for a given turn (`has_human_turn` check), so `bind_tools()` gets
a proper conversational message list. Keep that check — without it, the model won't actually see
the patient's question on later tool-loop iterations, only the `ToolMessage` results.