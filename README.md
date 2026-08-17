# AI-Powered Personal Health Intelligence Companion

**Final Year Project (BSCS) — AI/ML Engineering Track**

A conversational medical AI system that combines a fine-tuned medical LLM, retrieval-augmented generation, multimodal OCR, and persistent structured patient memory to give patients holistic, history-aware health guidance — not just single-turn symptom lookup.

> **Scope note:** The current implementation is **100% English**. Urdu/Roman-Urdu support described in the original proposal is a future-work item, not part of the present build (see [Deviations from the Original Proposal](#deviations-from-the-original-proposal)).

---

## 1. Problem Statement

Patients — particularly in under-resourced healthcare systems — struggle to communicate their full medical context to doctors in a short consultation window. Decisions often get made on a few minutes of verbal symptom description, with no structured access to prior prescriptions, lab reports, lifestyle factors, or emotional state. Generic chatbot-style AI tools don't solve this: they answer the current message in isolation and forget everything the moment the session ends.

## 2. Solution Overview

This system is a **patient-memory-first medical assistant**. Every conversation turn:

1. Extracts and stores durable, structured facts about the patient (identity, symptoms, medications, lab results, lifestyle, emotional state) into a persistent memory store.
2. Decides — via an LLM router — whether the current query needs external medical knowledge (internal vector DB or live web search).
3. Generates a final, empathetic answer using a **domain-fine-tuned medical LLM**, grounded in the patient's accumulated history, any OCR'd documents, and retrieved medical context.

The result is a system that reasons **holistically** — cross-referencing active symptoms against current medications, lifestyle, and lab results — rather than answering each message as a stateless Q&A pair.

---

## 3. Core Technologies

| Layer | Technology | Notes |
|---|---|---|
| Diagnostic / Chat LLM | **BioMistral-7B, fine-tuned (QLoRA) on a 10K-sample medical instruction dataset** | Served locally via `llama.cpp` / GGUF (`llama_cpp_python`), exposed as an OpenAI-compatible endpoint and consumed through `langchain_openai.ChatOpenAI` |
| Orchestration / Router LLM | `openai/gpt-oss-120b` via **Groq** | Used for tool-routing (RAG decision) and structured-output memory extraction — fast, cheap, and reliable for tool-calling, keeping the fine-tuned model dedicated to the final diagnostic response |
| Agent Framework | **LangGraph** | Stateful, checkpointed multi-node graph (see [Architecture](#4-agent-architecture)) |
| Vector Database | **Qdrant (Cloud instance)** | Stores the medical knowledge base (disease info, MedQA, PubMed-derived content) for RAG |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` | Used for both RAG document retrieval and semantic memory-relevance ranking |
| Relational / Checkpoint DB | **PostgreSQL — Neon (Cloud, serverless/autosuspending)** | Backs (a) LangGraph's conversation checkpointer, (b) LangGraph's long-term memory `Store`, and (c) the SQLAlchemy `users` / `refresh_tokens` / `tokens` auth tables |
| OCR / Vision | **Groq-hosted Qwen VLM** (`qwen/qwen3.6-27b` via `langchain_groq.ChatGroq`) | Extracts structured clinical text (diagnosis, meds, lab values, vitals) from photographed prescriptions and lab reports |
| Web Search Fallback | SerpAPI | Corrective-RAG fallback when internal knowledge base retrieval is weak/insufficient |
| Backend API | **FastAPI** (async) | JWT + refresh-token auth, streaming chat, and agent endpoints |
| Frontend | **React 19 + Vite + Tailwind CSS v4** | Chat UI, conversation sidebar, auth modals |
| Testing / Eval | `pytest`, ROUGE, BERTScore, custom hallucination/grounding rubric | Compares fine-tuned-only vs. RAG-augmented responses |

---

## 4. Agent Architecture

The core reasoning engine is a **LangGraph state machine** with three primary nodes, compiled once at startup and checkpointed to Postgres so every conversation is resumable across requests.

```
                 ┌──────────────┐
   user input →  │   Remember   │   (gpt-oss-120b, structured output)
                 └──────┬───────┘
                        │ remembered_context (categorized patient memory)
                        ▼
                 ┌──────────────┐
                 │  RAG Router  │   (gpt-oss-120b, tool-calling)
                 └──────┬───────┘
                needs tools?  \
                     yes       no
                      │         │
                      ▼         │
                 ┌──────────┐   │
                 │  Tools   │   │   retrieve_medical_knowledge (Qdrant)
                 └────┬─────┘   │   search_web_medical (SerpAPI, corrective fallback)
                      │         │
                      ▼         ▼
                 ┌──────────────────┐
                 │  Chat (BioMistral)│   final empathetic, grounded answer
                 └──────────────────┘
                          │
                          ▼
                         END
```

### 4.1 Node 1 — `remember_node` (Memory Extraction)

Runs on **every** turn, before routing or retrieval.

- Loads the patient's existing memories from the Postgres-backed LangGraph `Store`.
- Sends the user's latest message (+ any OCR'd document text) to `gpt-oss-120b` with a **structured-output schema** (`MemoryDecision` → list of `MemoryItem`).
- Each extracted fact is tagged with a **category** (`identity`, `symptom`, `medication`, `lab_result`, `lifestyle`, `emotional`), a **status** (`active` / `resolved` / `historical`), and optional `severity` / `onset`.
- **Supersession, not duplication:** if a new fact updates an existing one (e.g. "headache is gone" → resolves a stored headache record; "headache is worse" → updates severity in place), the LLM references the original record's key via `supersedes_id` and the existing row is updated rather than a duplicate being appended. This keeps the patient's timeline as one-row-per-fact instead of accumulating contradictions.
- **Scaling (Phase 4 optimization):** identity facts always survive into the prompt; everything else is recency-prefiltered to a candidate pool, then ranked by cosine similarity (via the shared embedder) against the turn's topic, and capped — so a patient with hundreds of stored facts still produces a bounded, relevant context block instead of blowing the LLM's context window.

### 4.2 Node 2 — `rag_router_node` (Retrieval Routing)

- A **tool-calling** Groq LLM (`gpt-oss-120b`, `bind_tools`) decides whether the turn needs external medical knowledge.
- Triggers tools for any medical symptom/question; skips tools for purely conversational turns (greetings, thanks, identity questions already answered by memory).
- Emits LangGraph `tool_calls`, which are executed by a `ToolNode` wrapping two tools:
  - **`retrieve_medical_knowledge`** — direct vector search against the Qdrant `health_knowledge` collection (top-k, cosine similarity, score-thresholded).
  - **`search_web_medical`** — SerpAPI web search, used as a **corrective RAG** fallback when internal retrieval confidence is low or the query is out-of-distribution (e.g. "latest WHO guidance on mpox").

### 4.3 Node 3 — `biomistral_node` (Chat / Diagnosis Generation)

- The **only node that calls the fine-tuned BioMistral model.**
- Assembles a single clean system prompt containing:
  - Categorized **patient memory** (IDENTITY / ACTIVE SYMPTOMS / MEDICATIONS / LAB RESULTS / LIFESTYLE / EMOTIONAL STATE / RESOLVED HISTORY)
  - **OCR context** from any uploaded document (capped to avoid blowing the context window)
  - **Retrieved medical context** from the tools step
- Prompt explicitly instructs the model to **cross-reference categories** — e.g. check active symptoms against current medications before suggesting new ones, factor in lifestyle/emotional state, and weight severity/onset for urgency — rather than only pattern-matching the latest message.
- Guards against hallucination: never invents patient facts, never claims something was saved when memory writes failed, treats retrieved context as supporting (not guaranteed) information.

### 4.4 Why gpt-oss-120b for routing/memory but BioMistral for the final answer?

Tool-calling and structured JSON extraction benefit from a fast, reliable, general-purpose model — Groq's `gpt-oss-120b` is used here purely as **infrastructure** (deciding *whether* to retrieve, and *what facts* to store). The actual **medical answer generation** — the part that needs domain expertise — is delegated entirely to the **fine-tuned BioMistral model**, keeping the fine-tuning investment focused on the task it's specialized for.

---

## 5. Model Fine-Tuning

- **Base model:** BioMistral-7B (medical-domain pretrained Mistral variant)
- **Method:** QLoRA (parameter-efficient fine-tuning)
- **Training data:** 10,000 curated medical instruction samples
- **Serving:** Quantized GGUF checkpoint (Q4_K_M) served locally via `llama.cpp` / `llama-server`, exposed through an OpenAI-compatible `/v1` endpoint and consumed via `langchain_openai.ChatOpenAI` (`app/core/llm.py`)

### 5.1 Evaluation Methodology

`app/eval/` contains a full evaluation harness comparing **fine-tuned-only** vs. **RAG-augmented** generation across three query categories:

| Category | Count | Purpose |
|---|---|---|
| In-distribution | 30 | Standard clinical Q&A (symptoms, causes, diagnosis, treatment) with reference answers, scored via ROUGE-1/2/L and BERTScore |
| Out-of-distribution | 12 | Recency-dependent questions (e.g. latest WHO/CDC guidance) with no ground truth — tests whether corrective RAG web-fallback kicks in |
| Ambiguous | 8 | Vague, real-world patient phrasing ("I have chest pain.") — reference answers describe the *appropriate response pattern* (acknowledge + advise care) rather than a diagnosis |

Metrics captured per case: **ROUGE-1/2/L**, **BERTScore F1**, latency, retrieval decision, and average retrieval confidence score. A separate `hallucination_check.py` rubric grades groundedness of answers against retrieved sources on a 0–2 scale. Perplexity comparison (`run_perplexity.py`) further quantifies how much retrieved context improves the model's confidence on reference answers.

---

## 6. Persistent Patient Memory

Unlike a stateless chatbot, this system maintains a **structured, evolving patient profile** across sessions, stored in PostgreSQL (Neon) via LangGraph's `Store` abstraction, namespaced per patient.

Each memory record carries:
```
{
  "text": "Persistent headache, worsening",
  "category": "symptom",       // identity | symptom | medication | lab_result | lifestyle | emotional
  "status": "active",          // active | resolved | historical
  "severity": "moderate",
  "onset": "3 days ago"
}
```

When BioMistral generates a response, it sees this memory formatted into labeled sections and is explicitly instructed to reason **across** them — e.g. don't recommend a medication that conflicts with something in MEDICATIONS, weight LIFESTYLE and EMOTIONAL STATE alongside physical symptoms, and treat RESOLVED HISTORY as background only.

---

## 7. Multimodal Input (OCR)

- Endpoint: `POST /agent/invoke` accepts an optional `image_base64` (prescription photo, lab report scan).
- OCR is performed via **Groq's Qwen VLM** (`app/core/rag/ocr.py`), prompted to extract structured clinical fields (patient details, diagnosis, symptoms, vitals, lab values with units, medications with dosages, doctor instructions) while explicitly avoiding speculation on unreadable text (`[unclear]` marker).
- OCR runs **outside the LangGraph graph**, at the API layer — so raw Base64 image payloads never enter LangGraph checkpoints (which are persisted to Postgres). Only the extracted, structured text is passed into graph state, keeping checkpoint storage lean.
- Extracted OCR text feeds both `remember_node` (to persist medication/lab facts) and `biomistral_node` (to answer questions about the uploaded document directly).

---

## 8. Data Layer

| Concern | Backend | Details |
|---|---|---|
| Conversation state / checkpointing | **PostgreSQL (Neon, Cloud)** via `langgraph.checkpoint.postgres.PostgresSaver` | Every graph turn is checkpointed; the conversation sidebar (`/agent/threads`) is derived **directly from checkpoint rows** — there is no separate conversations table |
| Long-term patient memory | **PostgreSQL (Neon, Cloud)** via `langgraph.store.postgres.PostgresStore` | Namespaced `(patient_memories, patient_id)` key-value store for structured `MemoryItem` records |
| Vector search / RAG knowledge base | **Qdrant (Cloud)** | `health_knowledge` collection; retrieval filtered/scored via cosine similarity, `score_threshold=0.3` |
| App/auth data (users, tokens) | **PostgreSQL (Neon)** via async SQLAlchemy | Standard relational tables: `users`, `refresh_tokens`, `tokens` |

**Neon autosuspend handling:** Because Neon's free/serverless tier suspends an idle compute, both the checkpointer/store connection pool (`app/db/pool.py`) and the Qdrant client wrap queries in a bounded retry with backoff to transparently absorb the "cold start" reconnect without failing the user's request.

---

## 9. Authentication & Security

- **JWT access tokens** (short-lived, default 60 min) + **opaque refresh tokens** (7 days, SHA-256 hashed at rest, rotated on every refresh, individually revocable).
- Passwords hashed with **Argon2**.
- Enforced password policy (length, character classes, common-password blocklist) — shared source of truth between backend validation and frontend UX hints.
- Role-based access control via `require_role` dependency.
- Full register / login / refresh / logout flow with structured auth-event logging.

---

## 10. Backend API Surface

| Endpoint | Method | Purpose |
|---|---|---|
| `/auth/register`, `/auth/login`, `/auth/refresh`, `/auth/logout`, `/auth/me` | POST/GET | Auth lifecycle |
| `/agent/invoke` | POST | Main entry point — runs the full LangGraph pipeline (memory → routing → tools → BioMistral), optionally with an attached image for OCR |
| `/agent/threads` | GET | Sidebar list of the patient's conversations, derived from checkpoints |
| `/agent/threads/{thread_id}` | GET | Full transcript of one conversation |
| `/chat/stream` | POST | Lightweight streaming chat (no agent pipeline — direct BioMistral streaming) |
| `/rag/stream` | POST | Streaming chat with single-shot corrective RAG (no memory/agent graph) |

---

## 11. Project Structure

```
app/
├── agent/
│   ├── graph.py              # LangGraph state machine wiring (Remember → Router → Tools? → Chat)
│   ├── state.py               # AgentState TypedDict (shared graph state)
│   ├── tools.py                # retrieve_medical_knowledge, search_web_medical
│   ├── memory_schema.py       # MemoryItem / MemoryDecision Pydantic schemas
│   └── nodes/
│       ├── remember_node.py    # Memory extraction, supersession, semantic selection
│       ├── router_node.py      # RAG tool-routing
│       ├── biomistral_node.py  # Final answer generation
│       └── prompts.py          # BioMistral system prompt template
├── api/                        # FastAPI routers (auth, agent, chat, rag)
├── core/
│   ├── llm.py                  # BioMistral OpenAI-compatible client
│   ├── security.py             # JWT / Argon2 / refresh-token primitives
│   └── rag/
│       ├── embedder.py         # SentenceTransformer singleton
│       ├── qdrant_store.py     # Qdrant Cloud client + retrieval
│       ├── rag_tool.py         # Direct RAG wrapper
│       ├── corrective_rag.py   # Confidence-gated web-search fallback
│       └── ocr.py              # Groq Qwen VLM document extraction
├── db/                          # SQLAlchemy engine + LangGraph Postgres pools/lifespan
├── models/, schemas/            # ORM models & Pydantic request/response schemas
├── services/                    # agent_service, chat_service, rag_chat_service, conversation_service
├── eval/                        # Evaluation harness (ROUGE, BERTScore, perplexity, hallucination rubric)
└── tests/                       # Unit + integration + live test suites (pytest markers: unit/integration/live)

frontend/                        # React 19 + Vite + Tailwind chat UI
```

---

## 12. Local Setup

**Prerequisites:** Python 3.11+, Node.js, a running BioMistral GGUF server (`llama.cpp`), and Cloud credentials for Neon Postgres, Qdrant, and Groq.

```bash
# Backend
pip install -r requirements.txt --break-system-packages
cp .env.example .env   # fill in DATABASE_URL, QDRANT_URL, QDRANT_API_KEY,
                        #     GROQ_API_KEY, SERP_API_KEY, SECRET_KEY, LLM_BASE_URL, etc.
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

Required environment variables (see `app/config.py`): `DATABASE_URL`, `QDRANT_URL`, `QDRANT_API_KEY`, `HF_TOKEN`, `SECRET_KEY`, `GROQ_API_KEY`, `SERP_API_KEY`, `LLM_MODEL`, `LLM_BASE_URL`, `LLM_API_KEY`.

---

## 13. Testing

```bash
pytest -m unit           # fast, fully mocked
pytest -m integration     # ASGI client + mocked externals + sqlite
RUN_LIVE_TESTS=1 pytest -m live   # requires real Postgres/Qdrant/LLM
```

---

## 14. Deviations from the Original Proposal

| Proposal | Current Implementation |
|---|---|
| Urdu + English support | **English only** (current build); Urdu/Roman-Urdu is future work |
| Generic "fine-tuned medical LLM" | **BioMistral-7B, QLoRA fine-tuned on 10,000 samples** |
| "RAG pipeline" (unspecified backend) | **Qdrant Cloud** vector store + corrective web-search fallback (SerpAPI) |
| "PostgreSQL for persistent memory" | **Neon (managed Postgres Cloud)**, used for both LangGraph checkpoints and long-term memory `Store` |
| "OCR for handwritten prescriptions" | **Groq-hosted Qwen VLM**, structured clinical-field extraction |

---

## 15. Future Work

- Urdu / Roman-Urdu language support (translation layer or multilingual fine-tune)
- Voice input (speech-to-text) integration mentioned in the original proposal but not yet implemented
- Expanded fine-tuning dataset beyond 10K samples, with continued RAG-vs-fine-tuned comparative evaluation
- Doctor-facing dashboard / structured export of patient memory for real clinical handoff
- Formal clinical validation and hallucination-rate benchmarking at scale