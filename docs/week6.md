## Week 6 — Tool-Binding Agent Refactor

**Delete these files** (logic is absorbed into `tools.py` + `agent_node.py`):
`app/db/checkpointer.py`, `app/db/store.py`, `app/agent/nodes/router_node.py`, `rewriter_node.py`, `rag_node.py`, `reasoner_node.py`, `extraction_node.py`, `facts_node.py`, `memory_node.py`.

### Day 1 — Lifespan fix, schemas, tools

```python
# app/db/lifespan.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore

from app.config import settings

_conn_string = settings.DATABASE_URL.replace("postgresql+asyncpg", "postgresql")

checkpointer: PostgresSaver | None = None
store: PostgresStore | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global checkpointer, store

    checkpointer_cm = PostgresSaver.from_conn_string(_conn_string)
    checkpointer = checkpointer_cm.__enter__()
    checkpointer.setup()

    store_cm = PostgresStore.from_conn_string(_conn_string)
    store = store_cm.__enter__()
    store.setup()

    yield

    checkpointer_cm.__exit__(None, None, None)
    store_cm.__exit__(None, None, None)
```

```python
# app/schemas/agent.py
from pydantic import BaseModel, Field
from typing import Optional, Literal


class AgentRequest(BaseModel):
    patient_id: str
    query: str = ""
    image_base64: Optional[str] = None
    input_modality: Literal["text", "image"] = "text"


class AgentResponse(BaseModel):
    answer: str
    detected_lang: str
    needs_rag: bool = False
    save_memory: bool = False


class ToolCall(BaseModel):
    """Grammar-constrained agent decision. Kept deliberately small (5 fixed
    actions, flat action_input dict) — a 7B model reasons about this far
    more reliably than a deep/nested schema."""
    thought: str = Field(..., description="Brief reasoning for this step")
    action: Literal[
        "fetch_patient_facts",
        "retrieve_medical_knowledge",
        "save_patient_fact",
        "save_emotional_state",
        "final_answer",
    ]
    action_input: dict = Field(default_factory=dict)
    answer: Optional[str] = Field(None, description="Required when action is final_answer")
```

```python
# app/agent/tools.py
import uuid
from datetime import date
from langchain_core.tools import tool

from app.db.lifespan import store
from app.core.rag.corrective_rag import corrective_retrieve
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


@tool
def fetch_patient_facts(patient_id: str, query: str) -> str:
    """Retrieve relevant medical facts about a patient from persistent memory.
    Use when the patient refers to past symptoms or history."""
    if store is None:
        return "Memory store not available."
    try:
        items = store.search(("patient_facts", patient_id), query=query, limit=5)
        facts = [item.value for item in items]
        if not facts:
            return "No relevant patient history found."
        lines = [f"- {f['symptom']} (onset: {f['onset']}, status: {f['status']})" for f in facts]
        return "Known patient history:\n" + "\n".join(lines)
    except Exception as e:
        logger.exception("fetch_patient_facts failed")
        return f"Error retrieving patient facts: {e}"


@tool
def retrieve_medical_knowledge(query: str) -> str:
    """Retrieve evidence-based medical knowledge for diagnosis or treatment questions."""
    try:
        result = corrective_retrieve(query, top_k=5)
        docs = result["docs"]
        if not docs:
            return f"[Retrieval decision: {result['decision']}] No relevant documents found."
        lines = [f"[{d['source']}] {d['text'][:400]}" for d in docs[:3]]
        return f"[Retrieval decision: {result['decision']}]\n\n" + "\n\n".join(lines)
    except Exception as e:
        logger.exception("retrieve_medical_knowledge failed")
        return f"Error retrieving knowledge: {e}"


@tool
def save_patient_fact(patient_id: str, symptom: str, onset: str, status: str, source_message: str) -> str:
    """Save a newly reported symptom to the patient's persistent record."""
    if store is None:
        return "Memory store not available."
    key = f"{symptom}_{date.today().isoformat()}_{uuid.uuid4().hex[:4]}"
    try:
        store.put(("patient_facts", patient_id), key, {
            "symptom": symptom, "onset": onset, "status": status,
            "recorded_on": date.today().isoformat(), "source_message": source_message,
        })
        return f"Saved to patient record: {symptom} ({status})"
    except Exception as e:
        logger.exception("save_patient_fact failed")
        return f"Error saving fact: {e}"


@tool
def save_emotional_state(patient_id: str, emotion: str, intensity: str, trigger: str, source_message: str) -> str:
    """Save the patient's emotional state when they express anxiety, stress, or fear."""
    if store is None:
        return "Memory store not available."
    key = f"emotion_{date.today().isoformat()}_{uuid.uuid4().hex[:4]}"
    try:
        store.put(("patient_emotions", patient_id), key, {
            "emotion": emotion, "intensity": intensity, "trigger": trigger,
            "recorded_on": date.today().isoformat(), "source_message": source_message,
        })
        return f"Noted emotional state: {emotion} ({intensity})"
    except Exception as e:
        logger.exception("save_emotional_state failed")
        return f"Error saving emotion: {e}"


TOOLS = [fetch_patient_facts, retrieve_medical_knowledge, save_patient_fact, save_emotional_state]
```

### Day 2 — Agent node + graph (with the missing loop guard added)

```python
# app/agent/state.py
from typing import TypedDict, Optional, Annotated
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    patient_id: str
    raw_input: str
    has_image: bool
    image_base64: Optional[str]

    detected_lang: str
    english_query: str

    messages: Annotated[list, add_messages]
    tool_results: str
    tool_call_count: int   # NEW — loop guard, missing from the draft

    final_response: str
```

```python
# app/agent/nodes/agent_node.py
import json
from llama_cpp import LlamaGrammar
from langchain_core.messages import AIMessage

from app.core.llm import llm
from app.agent.state import AgentState
from app.schemas.agent import ToolCall
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

_SCHEMA = ToolCall.model_json_schema()
_GRAMMAR = LlamaGrammar.from_json_schema(json.dumps(_SCHEMA))
MAX_TOOL_CALLS = 4   # hard cap — prevents an unbounded agent<->tools loop

_TOOL_DOCS = """
1. fetch_patient_facts(query: str) — check past symptoms/history
2. retrieve_medical_knowledge(query: str) — look up diagnosis/treatment facts
3. save_patient_fact(symptom, onset, status, source_message) — record a NEW symptom
4. save_emotional_state(emotion, intensity, trigger, source_message) — record expressed emotion
5. final_answer(answer) — respond when you have enough information
"""

SYSTEM_PROMPT = """You are an empathetic Pakistani AI health companion.
Reason briefly, then pick ONE action. Use tools before diagnosing. Only
call final_answer once you have what you need.

For final_answer, format the response with:
**Diagnosis:** ...
**Confidence:** ...
**Medicines:** ...
**Diet:** ...
**Exercise:** ...
**When to see a doctor:** ...

Tools:
{tool_docs}

Patient ID: {patient_id}
Query: {query}

Tool results so far:
{tool_results}

Respond with ONLY the JSON object."""


def agent_node(state: AgentState) -> AgentState:
    count = state.get("tool_call_count", 0)

    # build tool_results from message history (replaces a separate post_tool node)
    messages = state.get("messages", [])
    tool_msgs = []
    for m in reversed(messages):
        if isinstance(m, AIMessage):
            break
        if getattr(m, "type", None) == "tool":
            tool_msgs.append(m)
    tool_results = (
        "\n\n".join(f"Tool '{m.name}' returned:\n{m.content[:500]}" for m in reversed(tool_msgs))
        if tool_msgs else "(No tool results yet)"
    )
    state["tool_results"] = tool_results

    # force a final answer once the loop budget is exhausted
    forced_final = count >= MAX_TOOL_CALLS

    prompt = SYSTEM_PROMPT.format(
        tool_docs=_TOOL_DOCS if not forced_final else "final_answer(answer) — you MUST use this now.",
        patient_id=state["patient_id"],
        query=state["english_query"],
        tool_results=tool_results,
    )

    output = llm(prompt, grammar=_GRAMMAR, max_tokens=500, temperature=0.3)
    raw = output["choices"][0]["text"]

    try:
        decision = ToolCall.model_validate_json(raw)
        if forced_final:
            decision.action = "final_answer"
            decision.answer = decision.answer or "Based on what you've shared, please consult a doctor for a full evaluation."
    except Exception:
        logger.exception(f"Agent validation failed: {raw!r}")
        decision = ToolCall(
            thought="Fallback.", action="final_answer",
            answer="I apologize, I encountered an issue. Please consult a doctor for urgent concerns.",
        )

    if decision.action == "final_answer":
        messages = messages + [AIMessage(content=decision.answer or "")]
    else:
        args = decision.action_input or {}
        args.setdefault("patient_id", state["patient_id"])
        if decision.action in ("save_patient_fact", "save_emotional_state"):
            args.setdefault("source_message", state["english_query"])
        messages = messages + [AIMessage(
            content=decision.thought,
            tool_calls=[{"id": f"tc_{count}", "name": decision.action, "args": args}],
        )]
        state["tool_call_count"] = count + 1

    state["messages"] = messages
    return state
```

```python
# app/agent/graph.py
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition

from app.agent.state import AgentState
from app.agent.nodes.ocr_node import ocr_node
from app.agent.nodes.translate_node import translate_in_node, translate_out_node
from app.agent.nodes.agent_node import agent_node
from app.agent.tools import TOOLS
from app.db.lifespan import checkpointer, store


def _route_after_agent(state: AgentState) -> str:
    return "tools" if tools_condition(state) == "tools" else "translate_out"


def build_health_agent():
    graph = StateGraph(AgentState)

    graph.add_node("ocr", ocr_node)                    # reused unchanged from Week 5
    graph.add_node("translate_in", translate_in_node)   # reused unchanged from Week 5
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(TOOLS))
    graph.add_node("translate_out", translate_out_node) # reused unchanged from Week 5

    graph.set_entry_point("ocr")
    graph.add_edge("ocr", "translate_in")
    graph.add_edge("translate_in", "agent")
    graph.add_conditional_edges("agent", _route_after_agent, {"tools": "tools", "translate_out": "translate_out"})
    graph.add_edge("tools", "agent")
    graph.add_edge("translate_out", END)

    return graph.compile(checkpointer=checkpointer, store=store)
```

`ocr_node`, `translate_in_node`, `translate_out_node` are your existing Week 5 files — genuinely unchanged, no need to touch them.

### Day 3 — Service layer, API, cleanup

```python
# app/services/agent_service.py
from starlette.concurrency import run_in_threadpool
from langchain_core.messages import AIMessage

from app.agent.graph import build_health_agent
from app.schemas.agent import AgentRequest, AgentResponse
from app.utils.logging_config import get_logger

logger = get_logger(__name__)
agent = build_health_agent()


def _build_initial_state(req: AgentRequest) -> dict:
    return {
        "patient_id": req.patient_id,
        "raw_input": req.query,
        "has_image": req.image_base64 is not None,
        "image_base64": req.image_base64,
        "detected_lang": "",
        "english_query": "",
        "messages": [],
        "tool_results": "",
        "tool_call_count": 0,
        "final_response": "",
    }


async def run_agent(req: AgentRequest) -> AgentResponse:
    initial_state = _build_initial_state(req)
    config = {"configurable": {"thread_id": req.patient_id}, "recursion_limit": 15}

    try:
        result = await run_in_threadpool(agent.invoke, initial_state, config)
    except Exception:
        logger.exception("Agent graph execution failed")
        raise

    tool_history = str(result.get("messages", []))
    return AgentResponse(
        answer=result["final_response"],
        detected_lang=result["detected_lang"],
        needs_rag="retrieve_medical_knowledge" in tool_history,
        save_memory=("save_patient_fact" in tool_history) or ("save_emotional_state" in tool_history),
    )
```

`recursion_limit=15` is LangGraph's own graph-level safety net, on top of `MAX_TOOL_CALLS` inside the node — belt and suspenders against the loop-hang risk.

`app/api/agent.py` is unchanged from Week 5. `app/main.py` just switches to the new lifespan:

```python
# app/main.py — only this changes
from app.db.lifespan import lifespan
app = FastAPI(title="Health Companion", lifespan=lifespan)
```

### Day 4 — Test the loop directly, not just the happy path

```python
# app/tests/test_week6_agent.py — run directly, not pytest, per your existing test convention
from app.services.agent_service import run_agent
from app.schemas.agent import AgentRequest
import asyncio

async def main():
    cases = [
        "hello, how are you",
        "I have had a fever and body pain for three days",
        "is this the same fever from before",       # tests fetch_patient_facts
        "I'm really scared about this",              # tests save_emotional_state
    ]
    for q in cases:
        r = await run_agent(AgentRequest(patient_id="test_patient_01", query=q))
        print(f"\nQ: {q}\nRAG: {r.needs_rag} | Saved: {r.save_memory}\nA: {r.answer[:200]}")

if __name__ == "__main__":
    asyncio.run(main())
```

Run this whole sequence on **one `patient_id`** so you can confirm the fever from case 2 actually gets recalled in case 3 — this is the real proof the fact-memory redesign works end to end.

### Day 5 — Wire into your existing React frontend (not Streamlit)

Since `ChatBox.jsx` currently only streams `/chat/stream`, add a second mode (or a toggle) that POSTs to `/agent/invoke` and renders `answer` directly — no streaming needed here since the graph only returns once the full loop finishes. This is genuinely a frontend task in your existing stack, not a new one.

---

## Updated Week 6 schedule

```
Day 1 → lifespan.py fix, schemas.py, tools.py — delete old checkpointer/store/node files
Day 2 → agent_node.py (with MAX_TOOL_CALLS guard) + graph.py (ToolNode + tools_condition)
Day 3 → agent_service.py (with recursion_limit) + main.py lifespan wiring
Day 4 → Multi-turn test script — confirm fact recall across turns, confirm loop terminates
Day 5 → Wire /agent/invoke into existing React ChatBox (not a new Streamlit app)
```

One thing to explicitly decide before Day 1: are you okay shipping the single-model ReAct loop as-is (with the iteration cap as the safety net), or do you want to revisit the two-model orchestrator idea given you now have ~3.5 weeks left? I'd lean toward shipping this version — it's a real, defensible architecture with the loop-bound fix in place — but it's your call given the timeline.