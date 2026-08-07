Good — this is a meaningful rework of Week 5's memory layer. Here's what changes and what doesn't.

**Unchanged, no need to touch:** `ocr_node.py`, `translate_node.py`, `router_node.py`, `rewriter_node.py`, `rag_node.py`, `reasoner_node.py`, `core/rag/corrective_rag.py`, `core/rag/qdrant_store.py`, `core/rag/embedder.py`, `core/rag/ocr.py`, `core/rag/translation.py`. All of that logic is independent of how memory/persistence works.

**Removed entirely:** `app/core/rag/memory_store.py`, `app/models/memory.py`, `app/agent/nodes/memory_node.py` (the manual `get_memory_node`/`save_memory_node`) — `PostgresSaver` + `PostgresStore` replace all of it.

## Day 1 — Checkpointer + Store setup

```python
# app/db/checkpointer.py
from langgraph.checkpoint.postgres import PostgresSaver
from app.config import settings

_conn_string = settings.DATABASE_URL.replace("postgresql+asyncpg", "postgresql")

checkpointer_cm = PostgresSaver.from_conn_string(_conn_string)
checkpointer = checkpointer_cm.__enter__()
checkpointer.setup()  # creates checkpoint tables on first run, no-ops after
```

```python
# app/db/store.py
from langgraph.store.postgres import PostgresStore
from app.config import settings

_conn_string = settings.DATABASE_URL.replace("postgresql+asyncpg", "postgresql")

store_cm = PostgresStore.from_conn_string(_conn_string)
store = store_cm.__enter__()
store.setup()  # creates store tables on first run, no-ops after
```

Both are module-level singletons, loaded once — same pattern as `core/llm.py`. `.setup()` is idempotent, safe to run on every startup.

## Day 2 — Router Agent

No change. Same grammar-constrained `router_node.py` from before.

## Day 3 — Extraction node (new — this is the actual fix for "fever a week ago")

```python
# app/schemas/agent.py — add this model alongside RouterDecision
from typing import Optional

class SymptomFact(BaseModel):
    has_fact: bool = Field(..., description="True if the message reports a symptom or medical fact worth remembering")
    symptom: Optional[str] = Field(None, description="The symptom or condition mentioned, e.g. 'fever'")
    onset: Optional[str] = Field(None, description="When it started, e.g. 'today', '3 days ago', or a date if stated")
    status: Optional[str] = Field(None, description="ongoing, resolved, or worsening, if mentioned")
```

```python
# app/agent/nodes/extraction_node.py
import json
from datetime import date
from llama_cpp import LlamaGrammar

from app.core.llm import llm
from app.agent.state import AgentState
from app.schemas.agent import SymptomFact
from app.db.store import store
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

_SCHEMA = SymptomFact.model_json_schema()
_GRAMMAR = LlamaGrammar.from_json_schema(json.dumps(_SCHEMA))

EXTRACTION_PROMPT = """Extract any symptom or medical fact from this message.
If none is mentioned, set has_fact to false.

Examples:
User: "I have had a fever since yesterday"
{{"has_fact": true, "symptom": "fever", "onset": "yesterday", "status": "ongoing"}}

User: "hello, how are you"
{{"has_fact": false, "symptom": null, "onset": null, "status": null}}

User: "my headache from last week is finally gone"
{{"has_fact": true, "symptom": "headache", "onset": "last week", "status": "resolved"}}

Now extract from this message:
User: "{query}"
Respond with ONLY the JSON object."""


def extraction_node(state: AgentState) -> AgentState:
    if not state.get("save_memory"):
        return state  # router already decided this turn isn't worth remembering

    output = llm(
        EXTRACTION_PROMPT.format(query=state["english_query"]),
        grammar=_GRAMMAR,
        max_tokens=80,
        temperature=0.1,
    )
    raw = output["choices"][0]["text"]

    try:
        fact = SymptomFact.model_validate_json(raw)
    except Exception:
        logger.exception(f"Extraction output failed validation: {raw!r}")
        return state

    if not fact.has_fact:
        return state

    namespace = ("patient_facts", state["patient_id"])
    key = f"{fact.symptom}_{date.today().isoformat()}"
    store.put(namespace, key, {
        "symptom": fact.symptom,
        "onset": fact.onset,
        "status": fact.status,
        "recorded_on": date.today().isoformat(),
        "source_message": state["english_query"],
    })

    return state
```

Namespacing by `("patient_facts", patient_id)` means every fact for a patient lives under one queryable bucket, independent of conversation turns — this is what makes "fever a week ago" survive regardless of how many chats happened since.

```python
# app/agent/nodes/facts_node.py
from app.agent.state import AgentState
from app.db.store import store


def fetch_facts_node(state: AgentState) -> AgentState:
    namespace = ("patient_facts", state["patient_id"])
    items = store.search(namespace, query=state["english_query"], limit=5)
    state["patient_facts"] = [item.value for item in items]
    return state
```

`store.search()` does semantic retrieval over stored facts if you've configured an embedder on the store (same `all-MiniLM-L6-v2` you're already running — check `PostgresStore.from_conn_string(..., index=...)` config for wiring that in); otherwise it falls back to a plain listing. Either way, this replaces `get_recent_memory`'s "last 3 turns" with "facts relevant to *this* query," which is the actual fix.

```python
# app/agent/state.py — add one field
class AgentState(TypedDict):
    # ...unchanged fields...
    patient_facts: list[dict]   # new
```

## Day 4 — Reasoner update + graph reassembly

```python
# app/agent/nodes/reasoner_node.py — only _format_context/_format_memory replaced, generation logic unchanged
def _format_facts(facts: list[dict]) -> str:
    if not facts:
        return ""
    lines = [f"- {f['symptom']} (onset: {f['onset']}, status: {f['status']})" for f in facts]
    return "Known patient history:\n" + "\n".join(lines)

# inside reasoner_node(), replace the old _format_memory(...) call with:
facts_block = _format_facts(state.get("patient_facts", []))
if facts_block:
    parts.append(facts_block)
```

```python
# app/agent/graph.py — rewired: memory nodes removed, extraction + facts added, compiled with checkpointer + store
from langgraph.graph import StateGraph, END

from app.agent.state import AgentState
from app.agent.nodes.ocr_node import ocr_node
from app.agent.nodes.translate_node import translate_in_node, translate_out_node
from app.agent.nodes.router_node import router_node
from app.agent.nodes.facts_node import fetch_facts_node
from app.agent.nodes.rewriter_node import query_rewriter_node
from app.agent.nodes.rag_node import rag_node
from app.agent.nodes.reasoner_node import reasoner_node
from app.agent.nodes.extraction_node import extraction_node
from app.db.checkpointer import checkpointer
from app.db.store import store


def _route_after_router(state: AgentState) -> str:
    return "rewrite" if state["needs_rag"] else "reasoner"


def build_health_agent():
    graph = StateGraph(AgentState)

    graph.add_node("ocr", ocr_node)
    graph.add_node("translate_in", translate_in_node)
    graph.add_node("router", router_node)
    graph.add_node("fetch_facts", fetch_facts_node)
    graph.add_node("rewrite", query_rewriter_node)
    graph.add_node("rag", rag_node)
    graph.add_node("reasoner", reasoner_node)
    graph.add_node("extract_facts", extraction_node)
    graph.add_node("translate_out", translate_out_node)

    graph.set_entry_point("ocr")
    graph.add_edge("ocr", "translate_in")
    graph.add_edge("translate_in", "router")
    graph.add_edge("router", "fetch_facts")
    graph.add_conditional_edges(
        "fetch_facts", _route_after_router, {"rewrite": "rewrite", "reasoner": "reasoner"}
    )
    graph.add_edge("rewrite", "rag")
    graph.add_edge("rag", "reasoner")
    graph.add_edge("reasoner", "extract_facts")
    graph.add_edge("extract_facts", "translate_out")
    graph.add_edge("translate_out", END)

    return graph.compile(checkpointer=checkpointer, store=store)
```

Compiling with `checkpointer=checkpointer` is what gives you automatic conversation continuity — the full `AgentState` (including `recent_memory`-equivalent context from prior turns) is persisted and reloaded per `thread_id` without any manual DB query on your part.

## Day 5 — Service layer: thread_id wiring + test

```python
# app/services/agent_service.py — only the invoke call changes
async def run_agent(req: AgentRequest) -> AgentResponse:
    initial_state = _build_initial_state(req)
    config = {"configurable": {"thread_id": req.patient_id}}

    try:
        result = await run_in_threadpool(agent.invoke, initial_state, config)
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

`api/agent.py` and `schemas/agent.py`'s `AgentRequest`/`AgentResponse` shapes stay as they were — no change needed there.

## Updated Week 5 schedule

```
Day 1 → checkpointer.py + store.py — Postgres setup, verify tables created
Day 2 → Router agent (unchanged from before)
Day 3 → SymptomFact schema + extraction_node.py + facts_node.py
         Test extraction on 15-20 messages, verify store.put()/search() work
Day 4 → reasoner_node facts formatting + graph.py rewired with
         checkpointer + store compiled in
         Full end-to-end test: same patient_id across multiple invoke()
         calls, confirm checkpointer resumes state and facts persist
Day 5 → agent_service.py thread_id wiring
         Test: report a symptom, have several unrelated turns, then ask
         about it again — confirm it's still retrievable
```

One thing worth testing explicitly on Day 4, since it's the whole point of this rework: run a fake "week later" scenario — save a fact, run 5+ unrelated turns, then ask a question that should surface the old fact — and confirm `fetch_facts_node` actually returns it. That's the concrete proof this now does what your proposal claims.