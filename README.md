# Health Intelligence Companion

A full-stack medical Q&A application powered by a fine-tuned **BioMistral-7B** language model running locally via `llama-cpp-python`, augmented with a **Corrective Retrieval-Augmented Generation (Corrective RAG)** pipeline over a Qdrant vector store. Users sign up, verify their email, and chat with an AI health assistant that streams responses token-by-token.

At its core the app runs a **LangGraph health agent** (`/agent/invoke`) that chains OCR, multilingual translation, RAG retrieval, and long-term per-patient memory into a single multi-node pipeline — the preferred path over the raw streaming endpoints.

Built as a final-year project (FYP 2026): the base model was fine-tuned with **QLoRA** on 10,000 balanced medical samples and quantized to GGUF (`Q4_K_M`) so it runs efficiently on CPU.

> ⚠️ **Disclaimer:** This application provides general health information only and does not constitute medical advice. Always consult a qualified healthcare professional for medical concerns.

---

## Features

- 🤖 **LangGraph agent (`/agent/invoke`)** — multi-node pipeline with automatic conversation continuity (checkpointer) and persistent per-patient symptom memory (store), with structured output enforced by llama.cpp grammars
- 💬 **Streaming chat** — token-by-token responses with a custom in-app Markdown renderer (code blocks, bold/italic, auto-linked URLs, copy buttons)
- 🔍 **Corrective RAG (`/rag/stream`)** — retrieves medical context from a Qdrant vector store, evaluates retrieval quality, and falls back to / augments with live web search when the local context is weak
- 🌍 **Multilingual** — queries in non-English languages (e.g. Urdu) are auto-detected, translated to English for the pipeline, and the answer is translated back
- 🖼️ **Image support** — optional image input is run through OCR (`tesseract`) and the extracted text is folded into the query
- 🔐 **Full auth lifecycle** — register, login, refresh-token rotation, profile updates, password change/reset, email verification
- 🛡️ **Token-based security** — short-lived JWTs with `token_version` invalidation, opaque SHA-256-hashed refresh/reset/verify tokens, Argon2 password hashing
- 🔒 **Enforced password policy** — server-side validation (length, case, digits, specials, common-password blocklist) mirrored in the UI
- 🎨 **Dark, responsive UI** — React 19 + Tailwind 4

---

## Tech Stack

| Layer          | Technology                                                                 |
|----------------|----------------------------------------------------------------------------|
| Agent framework| LangGraph + `langgraph-checkpoint-postgres` (checkpointer & store, psycopg) |
| Backend        | Python, FastAPI, Uvicorn, Pydantic v2, async SQLAlchemy + `asyncpg`       |
| LLM            | `llama-cpp-python` + BioMistral-7B GGUF (`Q4_K_M`)                        |
| Embeddings     | `sentence-transformers` (`all-MiniLM-L6-v2`)                              |
| Vector store   | Qdrant (cloud) + Web search fallback via SerpAPI                          |
| Database       | PostgreSQL (Neon, serverless)                                             |
| Translation    | `langdetect` + `deep-translator` (GoogleTranslator)                       |
| OCR            | `pytesseract` (Tesseract)                                                 |
| Auth           | JWT (`python-jose`), opaque tokens, Argon2 (`argon2-cffi`)                |
| Frontend       | React 19, Vite 8, Tailwind 4, ESLint                                      |

---

## Getting Started

### Prerequisites

- **Python 3.11+** with a conda (or venv) environment
- **Node.js 18+** and npm
- The fine-tuned **BioMistral-7B GGUF model** (see [Model Setup](#model-setup))
- A **Qdrant** instance with the `health_knowledge` collection populated
- A **PostgreSQL** database (the project uses Neon serverless Postgres)
- **Tesseract** OCR engine (for the agent's image input) — `choco install tesseract` / `apt install tesseract-ocr`
- Network access to **Google Translate** (used by the agent's multilingual nodes)

### 1. Backend

```bash
# Create and activate an environment
conda create -n ft-project python=3.11
conda activate ft-project

# Install dependencies (includes the RAG, agent, translation, and OCR stacks)
pip install -r requirements.txt

# Configure environment — copy the required keys into a .env at the repo root
# (see Environment Variables below)

# Tesseract is required for the image/OCR node (installed separately)
#   Windows: choco install tesseract   |   Ubuntu: sudo apt install tesseract-ocr

# Run the API server (http://localhost:8000)
uvicorn app.main:app --reload
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev     # http://localhost:5173
```

The frontend calls `http://localhost:8000` (hardcoded as the API base in `src/utils/api.js`, `src/context/AuthContext.jsx`, and `src/components/ChatBox.jsx`).

---

## Environment Variables

All configuration is read from a `.env` file at the repo root via `pydantic-settings`. The backend **validates the following on startup**:

```env
# Database (PostgreSQL/Neon)
DATABASE_URL=postgresql+asyncpg://<user>:<password>@<host>/<dbname>

# Qdrant vector store
QDRANT_URL=<your-qdrant-url>
QDRANT_API_KEY=<your-qdrant-api-key>

# Auth & embeddings
SECRET_KEY=<a-long-random-secret>
HF_TOKEN=<huggingface-token>      # used to fetch the embedding model

# Web-search fallback (Corrective RAG correction step)
SERP_API_KEY=<your-serpapi-key>

# Optional — email delivery (dev mode logs emails to console when unset)
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=
```

> ⚠️ **Known config drift:** `app/config.py` `Settings` defines `DATABASE_URL`, `QDRANT_URL`, `QDRANT_API_KEY`, `HF_TOKEN`, `SECRET_KEY`, and `SERP_API_KEY` — but **not** `GROQ_API_KEY`, even though `app/main.py:validate_settings` still reads `settings.GROQ_API_KEY`. With `extra="ignore"` this raises `AttributeError` at startup, so the server will not boot until `GROQ_API_KEY` is added back to `Settings` (or dropped from `validate_settings`). This is tracked for the next cleanup pass.

Optional tuning via `app/config.py`:

| Variable                     | Default                                    | Purpose                                  |
|------------------------------|--------------------------------------------|------------------------------------------|
| `MODEL_PATH`                 | `C:\Users\jason\.cache\models\biomistral-Q4_K_M.gguf` | Path to the GGUF model file |
| `ACCESS_TOKEN_EXPIRE_MINUTES`| `15`                                       | JWT access-token lifetime               |
| `REFRESH_TOKEN_EXPIRE_DAYS`  | `7`                                        | Refresh-token lifetime                  |
| `RESET_TOKEN_EXPIRE_HOURS`   | `1`                                        | Password-reset token TTL                |
| `VERIFY_TOKEN_EXPIRE_HOURS`  | `48`                                       | Email-verify token TTL                  |
| `CORS_ORIGINS`               | `["http://localhost:5173"]`                | Allowed frontend origins                |

> The database schema is created automatically on startup from the SQLAlchemy models (`Base.metadata.create_all`). No manual migrations are required.

---

## Model Setup

Chat runs against the locally fine-tuned **BioMistral-7B** model in GGUF format. The model loads once at server startup (`app/core/llm.py`).

1. Obtain the `biomistral-Q4_K_M.gguf` file (the fine-tune pipeline is documented in [`docs/solution.md`](docs/solution.md) and [`docs/training-report.md`](docs/training-report.md)).
2. Place it anywhere on disk and point `MODEL_PATH` at it in `.env` — or put it at the default path in `app/config.py`.

---

## Architecture

The backend follows a layered layout: `api/` (routers) → `schemas/` (Pydantic request/response) → `services/` (business logic) → `models/` (SQLAlchemy) + `core/` (LLM, security, password policy, RAG) + `utils/` (email, logging). Auth dependencies live in `app/deps.py`.

### Streaming chat (the non-obvious part)

`app/core/llm.py` loads the GGUF model **at import time** (module-level `llm = Llama(...)`), so server startup is slow, and `llama_cpp`'s API is synchronous.

Both chat endpoints (`app/services/chat_service.py:stream_chat` and `app/services/rag_chat_service.py:stream_rag_chat`) bridge that sync generator to async with the same pattern:

1. An `asyncio.Queue` is created on the event loop.
2. A `producer` runs in a **thread executor** (`loop.run_in_executor`), pushes each content delta into the queue via `loop.call_soon_threadsafe`, and finishes with a sentinel (or an exception object on failure).
3. An async `consumer` yields queue items — the sentinel signals end-of-stream, an exception object yields a `\n\nServer Error` and returns.

Keep blocking LLM / Qdrant calls off the event loop — never call `llm.create_chat_completion` directly from an async route.

### Corrective RAG pipeline (`/rag/stream`)

`stream_rag_chat` prepends a retrieval step to the plain chat bridge: it takes the last user message, runs `app/core/rag/corrective_rag.py:corrective_retrieve`, builds an augmented prompt via `_build_prompt` (inlines up to 3 doc texts, truncated to 300 chars each), replaces the final user turn with the augmented prompt, then streams the LLM completion.

`corrective_retrieve(query, top_k=5)` is a three-stage Corrective RAG pipeline:

1. **Retrieve** — `app/core/rag/qdrant_store.py:retrieve` embeds the query with a singleton `SentenceTransformer` (`all-MiniLM-L6-v2`, loaded once via `get_embedder()`), queries the `health_knowledge` Qdrant collection (`score_threshold=0.3`, optional `category` payload filter), and returns docs with `text`, `source`, `category`, `score`.
2. **Evaluate** — `evaluate_relevance` classifies retrieval as `correct` / `ambiguous` / `incorrect` via score thresholds (`RELEVANCE_THRESHOLD = 0.5` on max score, `AMBIGUOUS_THRESHOLD = 0.35` on avg score).
3. **Correct** — on `incorrect`, the weak local context is **replaced** with SerpAPI Google results (prepended before the retrieved docs); on `ambiguous`, web results are **appended** to **augment** it. Returns the top-5 docs, the `decision`, and the average retrieval score.

### LangGraph health agent (`/agent/invoke`)

The newest and preferred path (`app/agent/`). `build_health_agent()` compiles a `StateGraph(AgentState)`, served by `app/services/agent_service.py:run_agent` via `run_in_threadpool(agent.invoke, ...)` (LangGraph's sync API must stay off the event loop, the same pattern as the streaming bridge). The `thread_id` is the `patient_id`, so every patient gets its own conversation thread.

Node pipeline (`app/agent/graph.py`):

```
ocr → translate_in → router → fetch_facts → (needs_rag?) rewrite → rag → reasoner → extract_facts → translate_out → END
```

- **`ocr`** — if an `image_base64` is supplied, runs `pytesseract` (`app/core/rag/ocr.py`) and appends the extracted text to `raw_input`.
- **`translate_in` / `translate_out`** — detect the input language (`langdetect`) and round-trip non-English queries through GoogleTranslate (`app/core/rag/translation.py`); the answer is translated back to the source language.
- **`router`** — decides `needs_rag` (is this a factual medical question?) and `save_memory` (is it worth remembering?) via an LLM call constrained by a llama.cpp **grammar** compiled from the `RouterDecision` Pydantic schema, so the model physically cannot emit invalid JSON. Fails safe to `needs_rag=True, save_memory=True`.
- **`fetch_facts`** — searches the per-patient memory store for prior symptoms (`app/db/store.py`, namespace `("patient_facts", patient_id)`).
- **`rewrite` → `rag`** — only reached when `needs_rag` is true: the query rewriter clarifies it, then `rag` reuses the same `corrective_retrieve`.
- **`reasoner`** — builds the final prompt from patient facts + retrieved docs and generates the answer with `llm.create_chat_completion`.
- **`extract_facts`** — when the router has `save_memory`, extracts a `SymptomFact` (also grammar-constrained) and stores it under the patient's fact namespace, so a symptom like "fever last week" survives across unrelated turns.

**Automatic memory, no manual queries:** the graph is compiled with a LangGraph **checkpointer** (`app/db/checkpointer.py`, `PostgresSaver`) and **store** (`app/db/store.py`, `PostgresStore`). The checkpointer persists the whole `AgentState` per `thread_id`, giving conversation continuity; the store provides long-term fact retrieval. Both are module-level singletons (`setup()` is idempotent) that rewrite `postgresql+asyncpg` → `postgresql` on `DATABASE_URL` because LangGraph uses psycopg. This replaced the old hand-rolled `get_memory`/`save_memory` nodes.

### Auth & tokens (`app/core/security.py`)

- **Access tokens:** short-lived JWTs (default 15 min) carrying a `token_version` claim.
- **Opaque tokens:** refresh, password-reset, and email-verify tokens are random `secrets.token_urlsafe(48)` values; only their **SHA-256 hash** is stored in the DB (`refresh_tokens`, `tokens` tables). Verification is constant-time via `secrets.compare_digest`. Because hashes can't be reversed, refresh/reset/verify lookups **scan all matching rows and hash-compare** (an intentional O(n) trade-off).
- **Revocation:** bumping a user's `token_version` (on password change/reset) invalidates all outstanding JWTs via `app/deps.py:get_current_user`. Refresh tokens are rotated (marked `revoked` after use).
- Password hashing uses argon2 (`argon2-cffi`). `require_role(*roles)` in `deps.py` provides role-gating.

### Password policy

`app/core/password_policy.py` is the **source of truth** for password strength (length, case, digit, special char, common-password blocklist). The backend enforces it in `app/schemas/auth.py` via a `model_validator` on register/reset/change schemas; the frontend `RegisterModal` mirrors these rules for UX only. Change rules here, then update the mirror.

### DB & email

- `app/db/session.py`: async engine tuned for Neon — `pool_pre_ping=True` and `pool_recycle=300` (seconds) to survive idle connection drops; `connect_args={"timeout": 60}`. Sessions via `async_sessionmaker(…, expire_on_commit=False)`.
- `app/utils/email.py`: when `SMTP_HOST` is empty (dev), emails are **logged to console** instead of sent. Set the `SMTP_*` vars to activate real sending.
- `app/utils/logging_config.py`: `get_logger()` writes to console + `logs.txt`; `log_auth_event()` emits structured auth lines.

---

## Project Structure

```
├── app/                      # FastAPI backend
│   ├── agent/                # LangGraph health agent (graph, state, nodes/)
│   ├── api/                  # Routers: auth, chat, rag, agent
│   ├── core/                 # LLM wrapper, security/tokens, password policy
│   │   └── rag/              # embedder, qdrant_store, corrective_rag, translation, ocr
│   ├── db/                   # Async engine + session, Base, LangGraph checkpointer + store
│   ├── models/               # SQLAlchemy models (User, RefreshToken, Token)
│   ├── schemas/              # Pydantic request/response models (incl. Agent schemas)
│   ├── services/             # Business logic (chat, RAG chat, agent service)
│   ├── tests/                # Standalone smoke scripts (not a pytest suite)
│   ├── utils/                # Email, logging
│   ├── deps.py               # Auth dependencies (get_current_user, require_role)
│   ├── config.py             # Settings (pydantic-settings)
│   └── main.py               # App entry point, lifespan, CORS
├── frontend/                 # React + Vite UI
│   └── src/
│       ├── components/       # ChatBox, Navbar, Login/Register modals
│       ├── context/          # AuthContext (useAuth)
│       └── utils/api.js      # JWT-aware fetch wrapper
├── docs/                     # Project notes & model-evaluation reports
└── requirements.txt          # Pinned Python dependencies
```

---

## API Overview

All routes live under the `app/api/` package.

### Auth — `/auth`

| Method | Endpoint                 | Description                                       |
|--------|--------------------------|---------------------------------------------------|
| POST   | `/auth/register`         | Create an account (returns tokens — auto-login)   |
| POST   | `/auth/login`            | Authenticate, receive access + refresh tokens     |
| POST   | `/auth/refresh`          | Rotate a refresh token for a new pair             |
| GET    | `/auth/me`               | Current user profile                              |
| PATCH  | `/auth/me`               | Update profile (`full_name`, `email`)             |
| PUT    | `/auth/me/password`      | Change password (signs out all sessions)          |
| DELETE | `/auth/me`               | Delete account (requires `confirmation: "DELETE"`) |
| POST   | `/auth/forgot-password`  | Email a reset link                                |
| POST   | `/auth/reset-password`   | Complete a password reset                         |
| POST   | `/auth/send-verification`| Send an email-verification link                   |
| GET    | `/auth/verify-email`     | Verify an email via one-time token                |

### Chat — `/chat`

| Method | Endpoint       | Description                                   |
|--------|----------------|-----------------------------------------------|
| POST   | `/chat/stream` | Stream a plain chat completion (no retrieval) |

```json
// POST /chat/stream
{
  "messages": [
    { "role": "user", "content": "What are the symptoms of vitamin D deficiency?" }
  ],
  "temperature": 0.7,
  "max_tokens": 1024
}
```

### RAG — `/rag`

| Method | Endpoint        | Description                                                   |
|--------|-----------------|---------------------------------------------------------------|
| POST   | `/rag/stream`   | Corrective RAG: retrieve context, then stream a completion    |

```json
// POST /rag/stream
{
  "messages": [
    { "role": "user", "content": "What are the symptoms of diabetes?" }
  ],
  "temperature": 0.7,
  "max_tokens": 1024
}
```

### Agent — `/agent`

| Method | Endpoint         | Description                                                                           |
|--------|------------------|---------------------------------------------------------------------------------------|
| POST   | `/agent/invoke`  | Run the full LangGraph health agent (translate → route → RAG → answer → remember)     |

```json
// POST /agent/invoke
{
  "patient_id": "user-42",
  "query": "مجھے بخار ہے"                      // or English, or attach an image
  // "image_base64": "<base64>…"               // optional — OCR'd before routing
}
```

```json
// 200 OK
{
  "answer": "I understand you have a fever…",
  "detected_lang": "ur",
  "needs_rag": true,
  "retrieval_decision": "correct",
  "sources": ["source-a.md", "source-b.md"],
  "save_memory": true
}
```

Interactive API docs are available at `http://localhost:8000/docs` (Swagger UI) when the server is running.

---

## Testing

The `app/tests/` directory contains **standalone smoke scripts** — not a `pytest` suite (`pytest`/`httpx` are not in `requirements.txt`). They hit real Qdrant / the real LLM, so run them against a live backend:

```bash
conda activate ft-project
python app/tests/test_qdrant.py          # retrieval from Qdrant
python app/tests/test_embedder.py        # embedding model loads and embeds
python app/tests/test_corrective_rag.py  # full Corrective RAG pipeline
python app/tests/test_rag_chat_stream.py # stream a RAG completion
python app/tests/test_chat.py            # POST /chat/stream via TestClient
python app/tests/test_auth.py            # register/login/refresh flow against live API
```

To exercise the agent against a live server: `curl -X POST http://localhost:8000/agent/invoke -H "Content-Type: application/json" -d '{"patient_id":"p1","query":"I have had a fever for two days"}'`.

---

## Documentation

The [`docs/`](docs/) directory contains research notes, the fine-tuning pipeline, and evaluation results:

- [`docs/solution.md`](docs/solution.md) — converting the merged fine-tuned model to GGUF
- [`docs/training-report.md`](docs/training-report.md) — QLoRA training + evaluation metrics (ROUGE, BERTScore, medical accuracy)
- [`docs/basemodel-vs-ftmodel.md`](docs/basemodel-vs-ftmodel.md) — base vs. fine-tuned comparison
- [`docs/agentic-rag-roadmap.md`](docs/agentic-rag-roadmap.md) — the Corrective RAG design roadmap
- [`docs/flow-charts/`](docs/flow-charts/) — agent-pipeline design notes: `agent-infra.md`, `router-node.md`, `rewriter.md`, `ocr-node.md`, `translate-node.md`, `translation.md`
- [`docs/urdu-translater.md`](docs/urdu-translater.md) — multilingual (Urdu) translation notes
- Plus weekly progress notes (`week1.md`–`week5-part2.md`) and the project roadmap

---

## License

All rights reserved. This project is developed for academic purposes as a final-year project.