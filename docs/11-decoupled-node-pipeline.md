# 📜 Technical Specification Plan: Decoupled Router Node Pipeline

## 🎯 Architectural Overview

To make tool calling robust, eliminate model failures on fine-tuned GGUF setups, and simplify codebase logic:

```
                  ┌───────────────────────┐
                  │      User Input       │
                  └───────────┬───────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │      Router Node      │
                  │   (langchain-groq)    │
                  │ Models: llama-3.3-70b │
                  └───────────┬───────────┘
                              │
                 ┌────────────┴────────────┐
                 │  Needs Tools?           │
                 ├─────────────────────────┤
                 │ YES          NO         │
                 ▼              ▼          │
          ┌─────────────┐   ┌──────────┐   │
          │ Tools Node  │   │          │   │
          │ (Executes   │   │          │   │
          │  Memory /   │   │          │   │
          │  RAG etc.)  │   │          │   │
          └──────┬──────┘   │          │   │
                 │          │          │   │
                 └────┬─────┘          │   │
                      ▼                │   │
          ┌───────────────────────┐    │   │
          │ Accumulate Tool       │    │   │
          │ Context Contextually  │    │   │
          └───────────┬───────────┘    │   │
                      └───────┬────────┘   │
                              ▼            
                  ┌───────────────────────┐
                  │    BioMistral Node    │
                  │    (Local GGUF LLM)   │
                  │ Response & Reasoning  │
                  └───────────┬───────────┘
                              │
                              ▼
                     [ Return Response ]

```

1. **Router Node (`llama-3.3-70b-versatile` or `gpt-oss-120b` via Groq):** Binds to tools via standard `.bind_tools()`. Evaluates tool needs and executes tools natively. Collects memory and context in plain string format.
2. **BioMistral Node (`llama_cpp` / local GGUF):** Receives plain system/human messages prepended with gathered tool contexts (Memory + RAG). Outputs the final response without JSON formatting or function calling constraints.

---

## 🛠️ Step-by-Step Implementation Guide

### Step 1: Update Environment Configuration

Ensure `langchain-groq` is present in your environment dependencies and `.env` variable configuration.

Add to `app/config.py`:

```python
GROQ_MODEL: str = "llama-3.3-70b-versatile" # Fast & reliable for free tool calling

```

---

### Step 2: Clean Up Agent State Schema

Simplify `app/agent/state.py` to handle tool result propagation cleanly without mess.

```python
# app/agent/state.py
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    patient_id: str
    ocr_context: str
    tool_results: str  # Plain accumulated text from tools
    raw_input: str
    messages: Annotated[list, add_messages]
    
    # Metadata flags
    needs_rag: bool
    retrieval_decision: str
    retrieved_docs: list[dict]
    saved_memory: bool
    
    # Final Output
    answer: str
    final_response: str

```

---

### Step 3: Define Node 1 — Router Node (`router_node.py`)

Create `app/agent/nodes/router_node.py`. The router uses `ChatGroq` to safely decide on tool execution and make function calls.

```python
# app/agent/nodes/router_node.py
import time
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import settings
from app.agent.tools import TOOLS
from app.agent.state import AgentState
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

# Initialize Groq LLM strictly for router/tool-calling duty
router_llm = ChatGroq(
    api_key=settings.GROQ_API_KEY,
    model_name=settings.GROQ_MODEL,
    temperature=0.0
).bind_tools(TOOLS)

ROUTER_SYSTEM_PROMPT = """You are an intelligent routing agent for a healthcare assistant.
Your job is to analyze the conversation and call appropriate tools ONLY if required:
1. Call 'fetch_patient_facts' if the user mentions past history/symptoms.
2. Call 'retrieve_medical_knowledge' if the user asks a specific medical/health query.
3. Call 'save_patient_fact' or 'save_emotional_state' if the user reports new symptoms or emotional distress.

If no tools are needed (e.g., greetings, small talk), do NOT call any tools.
Patient ID: {patient_id}
"""

def router_node(state: AgentState) -> AgentState:
    logger.info("▶ Router Node Started | patient=%s", state["patient_id"])
    
    system_text = ROUTER_SYSTEM_PROMPT.format(patient_id=state["patient_id"])
    messages = [SystemMessage(content=system_text)] + state.get("messages", [])
    
    # Fallback to appending raw_input if history is empty
    if not any(isinstance(m, HumanMessage) for m in messages):
        messages.append(HumanMessage(content=state["raw_input"]))

    response = router_llm.invoke(messages)
    
    # Append AIMessage (which may contain tool_calls) to LangGraph state
    return {"messages": [response]}

```

---

### Step 4: Define Tool Execution Context Formatter

Update tool handling in `app/agent/graph.py` to convert executed tool output into plain text context for BioMistral.

```python
# Function helper inside graph orchestration
def extract_tool_results(state: AgentState) -> dict:
    """Reads messages from state and collects plain context for BioMistral."""
    tool_msgs = [m for m in state.get("messages", []) if getattr(m, "type", None) == "tool"]
    
    extracted_text = []
    rag_used = False
    saved_memory = False
    
    for msg in tool_msgs:
        tool_name = getattr(msg, "name", "")
        extracted_text.append(f"--- Context from tool [{tool_name}] ---\n{msg.content}\n")
        
        if tool_name == "retrieve_medical_knowledge":
            rag_used = True
        if tool_name in ("save_patient_fact", "save_emotional_state"):
            saved_memory = True

    combined_results = "\n".join(extracted_text)
    return {
        "tool_results": combined_results,
        "needs_rag": rag_used,
        "saved_memory": saved_memory
    }

```

---

### Step 5: Define Node 2 — BioMistral Reasoning Node (`biomistral_node.py`)

Create `app/agent/nodes/biomistral_node.py`. It receives raw user input along with collected plain-text contexts.

```python
# app/agent/nodes/biomistral_node.py
import time
from langchain_core.messages import SystemMessage, HumanMessage
from app.agent.state import AgentState
from app.core.llm import llm  # Local BioMistral GGUF
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

BIOMISTRAL_PROMPT = """You are an empathetic Pakistani AI health companion.

Use the provided medical & patient context below (if available) to answer the user's health concerns.

\n\n
{ocr_context}

{tool_context}
\n\n

GUIDELINES:
- If the query is plain conversational/greeting, reply naturally in plain text.
- If it is a medical query, respond conversationally based on the context. You can recommend these things where helpful:
  - Possible diagnosis or insights
  - Lifestyle adjustments, diet, and exercise suggestions
  - Home care or general advice
  - Clear advice on when to consult a doctor
- Never invent facts outside the provided context.
"""

def biomistral_node(state: AgentState) -> AgentState:
    logger.info("▶ BioMistral Reasoning Node Started")
    
    ocr_str = f"OCR Document Context: {state.get('ocr_context')}" if state.get("ocr_context") else "No OCR text attached."
    tool_str = state.get("tool_results") or "No external context retrieved."
    
    formatted_system = BIOMISTRAL_PROMPT.format(
        ocr_context=ocr_str,
        tool_context=tool_str
    )
    
    messages = [
        SystemMessage(content=formatted_system),
        HumanMessage(content=state["raw_input"])
    ]
    
    # Single clean inference turn from BioMistral GGUF without JSON or tools overhead
    start = time.monotonic()
    response = llm.invoke(messages)
    logger.info("✓ BioMistral completed in %.2fs", time.monotonic() - start)
    
    answer_text = response.content.strip()
    
    return {
        "answer": answer_text,
        "final_response": answer_text,
        "messages": [response]
    }

```

---

### Step 6: Construct the LangGraph (`app/agent/graph.py`)

Re-assemble the graph architecture cleanly.

```python
# app/agent/graph.py
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition

from app.agent.state import AgentState
from app.agent.nodes.router_node import router_node
from app.agent.nodes.biomistral_node import biomistral_node
from app.agent.tools import TOOLS
from app.db.lifespan import checkpointer, store

tool_node = ToolNode(TOOLS)

def build_health_agent():
    graph = StateGraph(AgentState)

    # 1. Add Nodes
    graph.add_node("router", router_node)
    graph.add_node("tools", tool_node)
    graph.add_node("biomistral", biomistral_node)

    # 2. Set Entry Point
    graph.set_entry_point("router")

    # 3. Conditional Routing from Router Node
    graph.add_conditional_edges(
        "router",
        tools_condition,
        {
            "tools": "tools",  # Route to tools if Router outputted tool_calls
            END: "biomistral"  # Route directly to BioMistral if no tools called
        }
    )

    # 4. Route from Tools to BioMistral Reasoning Node
    graph.add_edge("tools", "biomistral")
    
    # 5. BioMistral completes the sequence
    graph.add_edge("biomistral", END)

    compiled = graph.compile(
        checkpointer=checkpointer,
        store=store
    )
    return compiled

```

---

## 📋 Summary Checklist for Qoder IDE Agent

| File Target | Tasks |
| --- | --- |
| **`app/config.py`** | Add `GROQ_MODEL = "llama-3.3-70b-versatile"` configuration. |
| **`app/agent/state.py`** | Simplify `AgentState` schema to hold `tool_results`. |
| **`app/agent/nodes/router_node.py`** | Create node leveraging `ChatGroq` bound with `TOOLS`. |
| **`app/agent/nodes/biomistral_node.py`** | Create node taking plain strings & calling local GGUF model cleanly. |
| **`app/agent/graph.py`** | Wire `Router` $\rightarrow$ `Tools` (Optional) $\rightarrow$ `BioMistral` $\rightarrow$ `END`. |