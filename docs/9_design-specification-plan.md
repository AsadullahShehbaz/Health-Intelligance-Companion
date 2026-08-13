# Design Requirement Specification (DRS)
## Project: AI-Powered Personal Health Intelligence Companion (Simplified Architecture)

This document specifies the technical design, system components, database schemas, interfaces, and data flow sequences for the simplified version of the Health Companion application. It acts as the engineering blueprint for the upcoming refactoring phase.

---

## 1. System Architecture & Components

The system is structured as a lightweight, clean 3-tier architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend Client                        │
│                 (Streamlit UI / REST Client)                │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP REST Requests
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                        │
│                                                             │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────┐  │
│  │  API Controller  │  │ Ingestion (OCR)  │  │   Auth    │  │
│  └────────┬─────────┘  └────────┬─────────┘  └─────┬─────┘  │
│           │                     │                  │        │
│           ▼                     ▼                  ▼        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                     Agent Service                     │  │
│  │       (LangGraph Controller + Thread Invoker)         │  │
│  └──────────────────────────┬────────────────────────────┘  │
└─────────────────────────────┼───────────────────────────────┘
                              │ Invoke State Graph
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   LangGraph Reasoning Layer                 │
│                                                             │
│        ┌──────────────┐             ┌──────────────┐        │
│   ┌───>│  Agent Node  ├────────────>│  Tools Node  │        │
│   │    └──────┬───────┘             └──────┬───────┘        │
│   │           │ (final_answer)             │                │
│   │           ▼                            │                │
│   └──────────END                           │                │
│                                            │                │
│           ┌────────────────────────────────┴───────────┐    │
│           ▼                                            ▼    │
│  ┌─────────────────┐ ┌─────────────────┐ ┌───────────┐      │
│  │ fetch_pat_facts │ │ retrieve_m_know │ │ save_fact │      │
│  └────────┬────────┘ └────────┬────────┘ └─────┬─────┘      │
└───────────┼───────────────────┼────────────────┼────────────┘
            │                   │                │
            ▼                   ▼                ▼
┌─────────────────────────────────────────────────────────────┐
│                       Data Storage                          │
│                                                             │
│   ┌──────────────────────────────────────────────────┐      │
│   │                    PostgreSQL                    │      │
│   │  - Users Table       - LangGraph PostgresSaver   │      │
│   │  - PostgresStore     - Thread Checkpoints        │      │
│   └──────────────────────────────────────────────────┘      │
│   ┌──────────────────────────────────────────────────┐      │
│   │                 Qdrant Vector DB                 │      │
│   │  - Medical Knowledge (PubMed / WHO guidelines)   │      │
│   └──────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### 1.1 FastAPI Controller Layer
* **[agent.py](file:///c:/Fine%20Tuning/code/app/api/agent.py):** Contains routes for invoking the agent and loading thread histories.
* **[auth.py](file:///c:/Fine%20Tuning/code/app/api/auth.py):** Simplified authentication router managing register/login operations.
* **[deps.py](file:///c:/Fine%20Tuning/code/app/deps.py):** Standard FastAPI security dependency injection to retrieve `current_user`.

### 1.2 Ingestion & Document Processing Layer
* **[ocr.py](file:///c:/Fine%20Tuning/code/app/core/rag/ocr.py):** Extracts raw text from base64 prescription images using Tesseract OCR. Executed synchronous-in-thread before graph invocation.

### 1.3 LangGraph Reasoning Layer
* **[graph.py](file:///c:/Fine%20Tuning/code/app/agent/graph.py):** Defines the single-loop state graph consisting only of `agent` and `tools` nodes.
* **[state.py](file:///c:/Fine%20Tuning/code/app/agent/state.py):** Streamlined typed state representation.
* **[agent_node.py](file:///c:/Fine%20Tuning/code/app/agent/nodes/agent_node.py):** System prompts, LLM parser, and RAG status updates.
* **[tools.py](file:///c:/Fine%20Tuning/code/app/agent/tools.py):** Registered Langchain tool wrappers executing vector DB retrievals or storing facts.

---

## 2. Database Schema Design

All application states (except the Qdrant vector index) reside in PostgreSQL.

### 2.1 Users Schema (`users` table)
This represents a simplified user structure:
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NULL,
    role VARCHAR(20) DEFAULT 'user' NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);
```

### 2.2 LangGraph PostgresSaver & PostgresStore Tables
LangGraph automatically initializes and maintains these tables inside PostgreSQL during [lifespan.py](file:///c:/Fine%20Tuning/code/app/db/lifespan.py#L31) startup:

1. **`checkpoints`**: Stores thread progress, variables, and history checkpoints.
2. **`writes`**: Tracks writes occurring during supersteps.
3. **`checkpoint_blobs`**: Serialized binary state data.
4. **`checkpoint_writes`**: Maps checkpoint writes.
5. **`store`**: Semantic store table used by `PostgresStore` for persistent memories. It holds:
   * `namespace`: Structured path partitions like `("patient_facts", patient_id)`.
   * `key`: Unique item identifiers.
   * `value`: JSON data representing patient facts or emotional logs.

---

## 3. Data Flow Sequences

### 3.1 Synchronous Request Flow (Symptom Processing & Reasoning)

```
[Patient Client]          [API Controller]           [Ingestion]           [Agent Service]          [LangGraph/LLM]
       │                         │                        │                       │                        │
       │─── POST /agent/invoke ─>│                        │                       │                        │
       │    (query, image)       │                        │                       │                        │
       │                         │── extract text ───────>│                        │                        │
       │                         │   (if image present)   │                        │                        │
       │                         │<── ocr text ───────────│                       │                        │
       │                         │                                                │                        │
       │                         │─────────────── run_agent(req, ocr_text) ──────>│                        │
       │                         │                                                │── agent.invoke() ─────>│
       │                         │                                                │   (initial_state)      │── Evaluate query
       │                         │                                                │                        │   in Urdu/English
       │                         │                                                │                        │   and check memory
       │                         │                                                │<── Execute tool calls ─│
       │                         │                                                │    (RAG / Fact save)   │
       │                         │                                                │── Tool results ───────>│
       │                         │                                                │                        │── Form final
       │                         │                                                │                        │   answer
       │                         │                                                │<── final_answer JSON ──│
       │                         │<────────────── return state variables ─────────│                        │
       │<── return AgentResponse ─│                                                │                        │
       │    (diagnosis, memory)  │                                                │                        │
```

---

## 4. Agent Prompts and Schema Definitions

### 4.1 Simplified Graph State ([state.py](file:///c:/Fine%20Tuning/code/app/agent/state.py))
```python
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    patient_id: str                     # Context identifier
    ocr_context: str                    # Parsed prescription text
    tool_call_count: int                # Loop guard counter
    messages: Annotated[list, add_messages] # Thread history reducer
    
    # Checkpoint variables to support sidebar queries
    raw_input: str                      # Raw client question
    final_response: str                 # Unified response container
    detected_lang: str                  # Detected query language
    needs_rag: bool                     # Flag if vector store hit
    retrieval_decision: str             # Correctness evaluation status
    retrieved_docs: list                # Output source references
```

### 4.2 System Prompt ([agent_node.py](file:///c:/Fine%20Tuning/code/app/agent/nodes/agent_node.py))
```
You are an empathetic Pakistani AI health companion.
Communicate directly and naturally in the language the patient uses—respond in Urdu (using Urdu script or Roman-Urdu) or English matching the input query's tone. Do not use intermediate translation.

Reason briefly, then pick ONE action. Use tools before diagnosing.
Only call final_answer once you have retrieved history or medical knowledge if necessary.

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
Attached Prescription OCR: {ocr_context}

Tool results so far:
{tool_results}

Respond with ONLY a valid JSON object matching this schema:
{{
    "thought": "Brief diagnostic reasoning step",
    "action": "retrieve_medical_knowledge" | "fetch_patient_facts" | "save_patient_fact" | "final_answer",
    "action_input": {{ "query": "search query" }} or {{ "answer": "final response string" }}
}}
```

---

## 5. Security & Authentication Specification

### 5.1 Simple JWT Token Strategy
* JWT tokens are short-to-medium-lived (e.g. 7 days expiration) and contain only user information and expiration timestamps.
* Token payload structure:
  ```json
  {
    "sub": "user_id_uuid_string",
    "exp": 1756543200
  }
  ```

### 5.2 Password Hashing Setup ([security.py](file:///c:/Fine%20Tuning/code/app/core/security.py))
Replace the complex `argon2-cffi` dependency with standard fast standard `bcrypt` hashing:
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

---

## 6. Implementation Checklist & Phase Mappings

| Refactoring Phase | Code Paths Modified | Verification Strategy |
|---|---|---|
| **Phase 1: Ingestion** | [agent.py](file:///c:/Fine%20Tuning/code/app/api/agent.py) | Upload mock prescription image, verify Tesseract output in FastAPI logs. |
| **Phase 2: Graph** | [graph.py](file:///c:/Fine%20Tuning/code/app/agent/graph.py), [state.py](file:///c:/Fine%20Tuning/code/app/agent/state.py) | Assert graph contains exactly 2 execution nodes (`agent`, `tools`). |
| **Phase 3: Prompt & Parser** | [agent_node.py](file:///c:/Fine%20Tuning/code/app/agent/nodes/agent_node.py) | Execute queries in Urdu script and Roman-Urdu, confirm Urdu replies. |
| **Phase 4: Persistence** | [agent_service.py](file:///c:/Fine%20Tuning/code/app/services/agent_service.py) | Verify thread recovery and sidebar loading functions work on PostgresSaver. |
| **Phase 5: Auth** | [auth.py](file:///c:/Fine%20Tuning/code/app/api/auth.py), [security.py](file:///c:/Fine%20Tuning/code/app/core/security.py) | Execute `/auth/login` and `/auth/register` endpoints; confirm deletion of opaque DB models. |
