# Implementation Spec: Remember → RAG → Chat Agent Architecture

**Audience:** Coding agent (Claude Code / autonomous engineer) implementing this against the existing repo (`app/agent/*`, `app/core/*`, `app/db/*`).
**Author intent:** Refactor the current single-router LangGraph pipeline into the 3-stage pipeline shown in the architecture diagram, reusing the Pydantic memory-decision pattern from `14-memory-store.ipynb`.

---

## 1. Goal — map diagram to code

Target pipeline (from the whiteboard diagram):

```
Request
   │
   ▼
Remember (gpt-oss-120b)  ──────────────┐
   │                                    │ writes to Postgres store
   ▼                                    │ (patient_memories namespace)
RAG (gpt-oss-120b) ⇄ Tools (Web Search, RAG)
   │
   ▼
Chat (llama serve fine_tuned_biomistral.gguf)
   │
   ▼
Response
```

Sub-graph for **Remember**:

```
user_id, last_message
        │
        ▼
    Decision  ──existing_memories──┐  (loaded from store first)
        │                          │
   is_new / should_write           │
      ┌────┴────┐
      ▼          ▼
   False    should_write new text (store.put)
```

This is **structurally identical** to `remember_node` in `14-memory-store.ipynb`, just swapped from `InMemoryStore` → the existing `PostgresStore` (`app/db/lifespan.py:store`), and namespaced per-patient instead of the notebook's `("user", user_id, "details")`.

### What changes vs. today's code

| Today (`app/agent/graph.py`) | Target |
|---|---|
| `router (Groq, tool-calling)` decides tools **and** does memory saves via explicit tools (`save_patient_fact`, `save_patient_profile`, `save_emotional_state`) | Split into two nodes: **Remember** (always runs first, pure extraction+dedup, no tool-calling) then **RAG/Router** (decides `retrieve_medical_knowledge` / `search_web_medical` only — no more memory-write tools) |
| Single `AgentState.tool_results` blob feeds `biomistral_node` | `biomistral_node` now also receives `remembered_context` (the full existing-memory list, always loaded, not just newly-written items) |
| Memory tools are LLM-tool-call driven (router decides *whether* to call `save_patient_fact`) | Memory extraction is **deterministic per turn** — Remember always runs, always loads existing memories, and *itself* decides new vs. duplicate via structured output (`MemoryDecision`), matching the diagram's dedicated Decision node |

This is a real architectural change, not a rename — **do not try to shoehorn this into the existing tool-calling loop**. Build the two nodes explicitly as instructed below.

---

## 2. New Pydantic models (from the notebook, adapted)

Create `app/agent/memory_schema.py`:

```python
# app/agent/memory_schema.py
"""Structured-output schema for the Remember node.

Directly ports MemoryItem / MemoryDecision from 14-memory-store.ipynb.
Kept in its own module (not agent/state.py) because these are LLM
structured-output contracts, not graph state.
"""
from typing import List

from pydantic import BaseModel, Field


class MemoryItem(BaseModel):
    text: str = Field(description="Atomic user/patient memory as a short sentence")
    is_new: bool = Field(
        description="True if this memory is NEW and should be stored. "
        "False if it duplicates/overlaps something already known."
    )


class MemoryDecision(BaseModel):
    should_write: bool = Field(description="Whether to store any memories this turn")
    memories: List[MemoryItem] = Field(
        default_factory=list,
        description="Atomic memories extracted from the user's latest message",
    )
```

Notes for the coding agent:
- This is a **verbatim structural port** of the notebook's `MemoryItem`/`MemoryDecision` — do not redesign the schema. The whole point of reusing it is that it's already validated to work with `.with_structured_output()` on `ChatGroq`.
- Do **not** put these in `app/schemas/agent.py` — that file is API request/response schemas (FastAPI response_model), a different concern from LLM structured-output contracts.

---

## 3. New node: `remember_node.py`

Create `app/agent/nodes/remember_node.py`:

```python
# app/agent/nodes/remember_node.py
"""Node 1 — Remember.

Runs before RAG/routing on every turn. Loads existing patient memories from
the Postgres store, asks gpt-oss-120b (via Groq, structured output) to
extract atomic facts from the user's latest message and flag which are
genuinely new, then writes only the new ones back to the store.

This mirrors 14-memory-store.ipynb's remember_node 1:1, adapted from
InMemoryStore to the app's PostgresStore and from MessagesState to
AgentState.
"""
import time
import uuid

from langchain_core.messages import SystemMessage

from app.agent.memory_schema import MemoryDecision
from app.agent.state import AgentState
from app.config import settings
from app.db.lifespan import store
from app.db.pool import run_with_retry
from app.utils.logging_config import get_logger
from langchain_groq import ChatGroq

logger = get_logger(__name__)

# Same model as the router — gpt-oss-120b via Groq, per the architecture
# diagram. Kept as a separate instance (not router_llm) because this one
# uses structured output, not tool-calling.
_memory_llm = ChatGroq(
    api_key=settings.GROQ_API_KEY,
    model_name=settings.GROQ_MODEL,   # "openai/gpt-oss-120b"
    temperature=0.0,
).with_structured_output(MemoryDecision)

MEMORY_NAMESPACE = "patient_memories"  # store namespace segment


def _namespace(patient_id: str) -> tuple:
    return (MEMORY_NAMESPACE, patient_id)


def _load_existing_memories(patient_id: str) -> list[str]:
    """Everything currently on file for this patient, as plain sentences."""
    try:
        items = run_with_retry(store.search, _namespace(patient_id), limit=200)
    except Exception:
        logger.exception("Failed to load existing memories | patient=%s", patient_id)
        return []
    texts = [item.value.get("data", "") for item in items if item.value.get("data")]
    return texts


def _format_existing(texts: list[str]) -> str:
    return "\n".join(f"- {t}" for t in texts) if texts else "(empty)"


REMEMBER_SYSTEM_PROMPT = """You are responsible for updating and maintaining accurate patient memory
for a healthcare companion system.

CURRENT PATIENT DETAILS (existing memories):
{existing_memories}

TASK:
- Review the patient's latest message.
- Extract patient-specific info worth storing long-term: identity/background
  facts (name, age, occupation, family, emergency contact, preferences),
  medical symptoms, onset/status, and emotional state when clearly expressed.
- For each extracted item, set is_new=true ONLY if it adds NEW information
  compared to CURRENT PATIENT DETAILS.
- If it is basically the same meaning as something already present, set
  is_new=false.
- Keep each memory as a short atomic sentence.
- No speculation; only facts stated by the patient.
- If there is nothing memory-worthy (e.g. a greeting, a question with no new
  personal info), return should_write=false and an empty list.
"""


def remember_node(state: AgentState) -> dict:
    patient_id = state["patient_id"]
    logger.info("▶ Remember Node Started | patient=%s", patient_id)

    if store is None:
        logger.warning("Memory store not available — skipping remember step")
        return {"remembered_context": "", "saved_memory": False}

    existing_texts = _load_existing_memories(patient_id)
    existing_block = _format_existing(existing_texts)

    user_message = (state.get("raw_input") or "").strip()
    if not user_message:
        logger.info("No user input to extract memories from | patient=%s", patient_id)
        return {
            "remembered_context": existing_block,
            "saved_memory": False,
        }

    system_msg = SystemMessage(content=REMEMBER_SYSTEM_PROMPT.format(existing_memories=existing_block))

    start = time.monotonic()
    try:
        decision: MemoryDecision = _memory_llm.invoke([
            system_msg,
            {"role": "user", "content": user_message},
        ])
    except Exception:
        logger.exception("Memory extraction failed | patient=%s", patient_id)
        # Fail open: don't block the turn on a memory-extraction error.
        return {"remembered_context": existing_block, "saved_memory": False}
    logger.info("✓ Remember LLM call finished in %.2fs", time.monotonic() - start)

    newly_written: list[str] = []
    if decision.should_write:
        for mem in decision.memories:
            if not mem.is_new:
                continue
            try:
                run_with_retry(
                    store.put,
                    _namespace(patient_id),
                    str(uuid.uuid4()),
                    {"data": mem.text},
                )
                newly_written.append(mem.text)
            except Exception:
                logger.exception(
                    "Failed to persist memory | patient=%s | text=%s",
                    patient_id, mem.text,
                )

    if newly_written:
        logger.info(
            "✓ Wrote %d new memories | patient=%s", len(newly_written), patient_id,
        )

    # Rebuild the context block including anything just written, so the
    # downstream RAG/router and Chat nodes see the fully up-to-date picture
    # without a second DB round-trip.
    final_texts = existing_texts + newly_written
    return {
        "remembered_context": _format_existing(final_texts),
        "saved_memory": bool(newly_written),
    }
```

Design decisions the coding agent should preserve:
- **Fail open, never block the turn.** If Groq/the store is unavailable, return the existing context (possibly empty) and move on — mirrors the resilience pattern already used in `app/agent/tools.py` (`_verified_put`, `run_with_retry`).
- **One LLM call per turn**, not one per fact — matches the notebook's single `memory_extractor.invoke(...)`.
- **No `source_message` / `onset` / `status` structured fields** like the old `save_patient_fact` tool. The notebook's model is deliberately looser (`text: str`), and the diagram's "Decision" node is a single atomic-fact-vs-duplicate check, not a rich schema. Keep it that way — do not silently reintroduce the old tool's rich fields.
- Reuse `run_with_retry` from `app/db/pool.py` for every store call, exactly as `app/agent/tools.py` does — do not write a new retry wrapper.

---

## 4. State changes — `app/agent/state.py`

Add two fields, keep everything else:

```python
class AgentState(TypedDict):
    patient_id: str
    ocr_context: str
    tool_results: str
    raw_input: str
    messages: Annotated[list, add_messages]

    # NEW — populated by remember_node, consumed by biomistral_node
    remembered_context: str   # formatted "- fact\n- fact" block, always present
    # saved_memory already exists below and is reused (now set by remember_node
    # instead of the old save_* tools)

    needs_rag: bool
    retrieval_decision: str
    retrieved_docs: list[dict]
    saved_memory: bool
    detected_lang: str

    answer: str
    final_response: str
```

`saved_memory` already exists in the schema and is already surfaced in `AgentResponse.save_memory` (`app/schemas/agent.py`) and in `conversation_service.py`'s checkpoint query (`checkpoint->'channel_values'->>'saved_memory'`) — **no schema/API changes needed there**, only the *source* of that flag moves from the tools node to `remember_node`.

---

## 5. Graph rewiring — `app/agent/graph.py`

### 5.1 Remove memory tools from the tool-calling surface

In `app/agent/tools.py`, remove `save_patient_fact`, `save_patient_profile`, and `save_emotional_state` from the `TOOLS` list (keep the functions defined for now, or delete them — see §8 migration notes). The router/RAG node's `TOOLS` list becomes:

```python
TOOLS = [
    fetch_patient_facts,        # keep? see note below
    fetch_patient_profile,      # keep? see note below
    retrieve_medical_knowledge,
    search_web_medical,
]
```

> **Open decision for the coding agent to resolve, not guess silently:** `fetch_patient_facts` / `fetch_patient_profile` become redundant once `remembered_context` is always injected into every turn (Remember always loads *everything*, unconditionally). Recommended: **remove them too** and rely purely on `remembered_context` in the Chat node's prompt — this matches the diagram, which shows no separate "fetch" tool, only the Decision block feeding forward. If you keep them for surgical/manual recall use cases, gate them behind a comment explaining why they're being kept despite being diagram-redundant.

### 5.2 New graph topology

```python
# app/agent/graph.py
def build_health_agent():
    graph = StateGraph(AgentState)

    graph.add_node("remember", remember_node)
    graph.add_node("rag_router", rag_router_node)   # renamed from router_node
    graph.add_node("tools", _run_tools)
    graph.add_node("chat", chat_node)               # renamed from biomistral_node

    graph.set_entry_point("remember")

    graph.add_edge("remember", "rag_router")

    graph.add_conditional_edges(
        "rag_router",
        _route_after_router,
        {
            "tools": "tools",
            "chat": "chat",
        },
    )

    graph.add_edge("tools", "chat")
    graph.add_edge("chat", END)

    compiled = graph.compile(checkpointer=checkpointer, store=store)
    logger.info("✓ Health agent graph compiled (remember → rag_router → tools? → chat → END)")
    return compiled
```

Renames (do these consistently across the codebase, including log messages and imports):

| Old name | New name | File |
|---|---|---|
| `app/agent/nodes/router_node.py` | keep filename, but rename function/prompt to reflect it's the **RAG router**, e.g. `rag_router_node` | same file |
| `app/agent/nodes/biomistral_node.py` | keep filename (it's still BioMistral under the hood), but the *diagram* calls it "Chat" — add a thin exported alias `chat_node = biomistral_node` at the bottom of the file, or rename the function to `chat_node` and update the one import in `graph.py`. **Prefer renaming the function** for clarity; update `app/agent/graph.py`'s import accordingly. |
| `ROUTER_SYSTEM_PROMPT` | Update its numbered rules — **delete rules 3 and 4** (save_patient_fact / save_patient_profile instructions), since those tools no longer exist on this node. Keep rules 1, 2, 5 (RAG/history retrieval) renumbered. |

### 5.3 `_route_after_router` — no change in logic, only naming

The existing `tools_condition`-based routing logic in `graph.py` is unaffected — it still just checks whether the LLM emitted `tool_calls`. Only rename the "biomistral" route key to "chat" to match the new node name, and update the dict passed to `add_conditional_edges`.

---

## 6. Chat node changes — `app/agent/nodes/biomistral_node.py`

The Chat node must now use `remembered_context` (always present, richer) instead of parsing patient-profile blocks out of `tool_results` (the old `_extract_patient_profile_block` hack existed *because* profile facts arrived embedded inside tool output strings — that hack goes away entirely).

```python
def biomistral_node(state: AgentState) -> dict:  # or rename to chat_node
    logger.info("▶ Chat Node Started")

    ocr_raw = (state.get("ocr_context") or "")[:_OCR_CHAR_LIMIT]
    ocr_str = f"OCR Document Context:\n{ocr_raw}" if ocr_raw else "No OCR text attached."

    tool_str = state.get("tool_results") or "No external context retrieved."
    remembered = state.get("remembered_context") or "(no known patient history yet)"

    formatted_system = BIOMISTRAL_PROMPT.format(
        ocr_context=ocr_str,
        tool_context=tool_str,
        patient_memory=remembered,     # NEW placeholder in the prompt template
    )

    user_question = (state.get("raw_input") or "").strip()

    messages = [
        SystemMessage(content=formatted_system),
        HumanMessage(content=user_question),
    ]
    # ... rest unchanged (llm.invoke, error handling, return dict)
```

Update `BIOMISTRAL_PROMPT` (both the inline copy in `biomistral_node.py` and the duplicate in `app/agent/nodes/prompts.py` — **these two currently drift; consolidate to one source of truth in `prompts.py` while you're in there**) to add a `{patient_memory}` section near the top, replacing the old "CRITICAL CONTEXT RULES" block that referenced tool-derived patient profiles:

```
Known patient memory (facts remembered across conversations):
{patient_memory}

CRITICAL CONTEXT RULES:
- Use the patient memory above naturally and accurately when relevant to the
  user's question. Do not say "I don't know anything about you" if the
  memory block above is non-empty.
- Never invent facts outside the provided context (memory, tool results, or OCR).
```

Delete `_extract_patient_profile_block` and its call site — it's dead code once `remembered_context` is injected directly.

---

## 7. `agent_service.py` — initial state

Add the new field to `_build_initial_state`:

```python
def _build_initial_state(req: AgentRequest, ocr_text: str = "") -> dict:
    return {
        "patient_id": req.patient_id,
        "raw_input": req.query,
        "ocr_context": ocr_text,
        "answer": "",
        "final_response": "",
        "detected_lang": "",
        "needs_rag": False,
        "retrieval_decision": "",
        "retrieved_docs": [],
        "saved_memory": False,
        "remembered_context": "",   # NEW
        "tool_results": "",
        "messages": [],
    }
```

No other change needed in `agent_service.py` — `run_agent`/`AgentResponse` construction is untouched since `saved_memory` already flows through unchanged (§4).

---

## 8. Migration notes for existing data & tests

1. **Old namespace `("patient_facts", patient_id)` and `("patient_profile", patient_id)` are not read by the new graph.** Any data already written there by the old tools becomes invisible to `remember_node` (which reads `("patient_memories", patient_id)`). Two options — pick one explicitly, don't leave it ambiguous:
   - **(A) One-off backfill script** (`scripts/backfill_memories.py`): read every key under `patient_facts`/`patient_profile` per patient, flatten each into a sentence (`f"{v['label']}: {v['value']}"` for profile, `f"{symptom} (status: {status})"` for facts), and `store.put` them into `patient_memories`.
   - **(B) Leave old data as-is, accept a cold start** for existing patients, and delete the old tools/namespaces outright.
   Recommend (A) if the DB already has real patient data worth preserving; otherwise (B) is simpler. State your choice in the PR description.

2. **`app/agent/tools.py` cleanup:** After removing the three save-tools from `TOOLS`, decide whether to delete the functions (`save_patient_fact`, `save_patient_profile`, `save_emotional_state`, `_normalize_field_key`, `MemoryPersistenceError`, `_verified_put`) or leave them unused. Recommend **deleting** them plus their tests in `app/tests/test_tools.py` (the `test_save_patient_profile_*` and `test_fetch_patient_profile_*` cases) once (A)/(B) above is decided, to avoid dead code with a false sense of coverage.

3. **`app/tests/test_week6_agent.py`** exercises the old fever/memory recall flow via `fetch_patient_facts`. Rewrite case 3 ("is this the same fever from before") to assert against `remembered_context` behavior instead — i.e., assert the *answer* references the previously stored fever fact, since there's no longer a dedicated fetch tool call to inspect in the trace.

4. **New unit tests to add** (`app/tests/test_remember_node.py`), following the existing `fake_store` fixture pattern from `test_tools.py`:
   - `test_remember_node_writes_new_fact` — first message about a new symptom → `store.put` called once, `saved_memory=True`.
   - `test_remember_node_skips_duplicate` — message restating an existing fact (mock `_memory_llm.invoke` to return `is_new=False`) → no `store.put` call, `saved_memory=False`.
   - `test_remember_node_handles_empty_input` — empty `raw_input` → returns existing context unchanged, no LLM call.
   - `test_remember_node_fails_open_on_llm_error` — mock `_memory_llm.invoke` to raise → node returns existing context, doesn't propagate the exception.
   - `test_remember_node_fails_open_on_store_unavailable` — `store=None` → returns empty context, no crash.

5. **`conversation_service.py`** needs no change — it already reads `saved_memory` generically from checkpoint `channel_values`; the source node changed but the checkpoint field name didn't.

---

## 9. Config — no new settings required

`settings.GROQ_MODEL` (`"openai/gpt-oss-120b"`) is reused for **both** `remember_node`'s `_memory_llm` and the RAG router's `router_llm` — this matches the diagram, which labels both boxes `gpt-oss-120b`. Do not add a second Groq model setting unless you deliberately want to run Remember and RAG-router on different models.

`settings.LLM_MODEL` / `LLM_BASE_URL` (the local llama-server / GGUF endpoint) continue to power only the Chat node, unchanged — matches the diagram's `llama serve fine_tuned_biomistral.gguf` label on the Chat box.

---

## 10. File-by-file checklist for the coding agent

- [ ] `app/agent/memory_schema.py` — **new file**, `MemoryItem`/`MemoryDecision` (§2)
- [ ] `app/agent/nodes/remember_node.py` — **new file** (§3)
- [ ] `app/agent/state.py` — add `remembered_context: str` (§4)
- [ ] `app/agent/tools.py` — remove memory-write tools from `TOOLS`; resolve deletion per §8.2
- [ ] `app/agent/nodes/router_node.py` — rename to RAG-router semantics, strip memory-tool instructions from prompt (§5.2)
- [ ] `app/agent/nodes/biomistral_node.py` — consume `remembered_context`, delete `_extract_patient_profile_block` (§6)
- [ ] `app/agent/nodes/prompts.py` — consolidate `BIOMISTRAL_PROMPT` here, add `{patient_memory}` placeholder (§6)
- [ ] `app/agent/graph.py` — new topology: `remember → rag_router → (tools?) → chat → END` (§5.2, §5.3)
- [ ] `app/services/agent_service.py` — add `remembered_context` to initial state (§7)
- [ ] `app/tests/test_remember_node.py` — **new file**, 5 unit tests (§8.4)
- [ ] `app/tests/test_tools.py` — remove/update tests tied to deleted tools (§8.2)
- [ ] `app/tests/test_week6_agent.py` — update case 3 assertions (§8.3)
- [ ] `scripts/backfill_memories.py` — **optional new file**, only if migration path (A) chosen (§8.1)

## 11. Out of scope (do not touch)

- OCR pipeline (`app/core/rag/ocr.py`), auth, `conversation_service.py` read path, `chat.py`/`rag.py` plain-chat routers — none of these are affected by this refactor and should not be modified.
- Corrective RAG scoring thresholds (`app/core/rag/corrective_rag.py`) — unrelated to this change.
- Frontend — no API shape changes (`AgentResponse` fields are unchanged), so no frontend work is required.