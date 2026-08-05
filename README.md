# Health Intelligence Companion

A full-stack medical Q&A application powered by a fine-tuned **BioMistral-7B** language model, running locally via `llama-cpp-python`. Users sign up, verify their email, and chat with an AI health assistant that streams responses token-by-token.

Built as a final-year project (FYP 2026): the base model was fine-tuned with **QLoRA** on 10,000 balanced medical samples and quantized to GGUF (`Q4_K_M`) so it runs efficiently on CPU.

> ⚠️ **Disclaimer:** This application provides general health information only and does not constitute medical advice. Always consult a qualified healthcare professional for medical concerns.

---

## Features

- 💬 **Streaming chat** — token-by-token responses with a custom in-app Markdown renderer (code blocks, bold/italic, auto-linked URLs, copy buttons)
- 🔐 **Full auth lifecycle** — register, login, refresh-token rotation, profile updates, password change/reset, email verification
- 🛡️ **Token-based security** — short-lived JWTs with `token_version` invalidation, opaque SHA-256-hashed refresh/reset/verify tokens, Argon2 password hashing
- 🔒 **Enforced password policy** — server-side validation (length, case, digits, specials, common-password blocklist) mirrored in the UI
- 🤖 **Local LLM inference** — the fine-tuned BioMistral-7B GGUF runs on your machine; no API calls for chat
- 🎨 **Dark, responsive UI** — React 19 + Tailwind 4

---

## Tech Stack

| Layer     | Technology                                                        |
|-----------|-------------------------------------------------------------------|
| Backend   | Python, FastAPI, Uvicorn, Pydantic v2                              |
| LLM       | `llama-cpp-python` + BioMistral-7B GGUF (`Q4_K_M`)                 |
| Database  | PostgreSQL (Neon, serverless) via async SQLAlchemy + `asyncpg`     |
| Auth      | JWT (`python-jose`), opaque tokens, Argon2 (`argon2-cffi`)         |
| Frontend  | React 19, Vite 8, Tailwind 4, ESLint                               |

---

## Getting Started

### Prerequisites

- **Python 3.11+** with a conda (or venv) environment
- **Node.js 18+** and npm
- The fine-tuned **BioMistral-7B GGUF model** (see [Model Setup](#model-setup))
- A **PostgreSQL** database (the project uses Neon serverless Postgres)

### 1. Backend

```bash
# Create and activate an environment
conda create -n ft-project python=3.11
conda activate ft-project

# Install dependencies
pip install -r requirements.txt

# Configure environment
# Copy the required keys into a .env file at the repo root (see below)

# Run the API server (http://localhost:8000)
uvicorn app.main:app --reload
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev     # http://localhost:5173
```

The frontend proxies requests to `http://localhost:8000` (hardcoded as the API base).

---

## Environment Variables

All configuration is read from a `.env` file at the repo root via `pydantic-settings`. The backend **requires** the following to start:

```env
# Database (PostgreSQL/Neon)
DATABASE_URL=postgresql+asyncpg://<user>:<password>@<host>/<dbname>

# Auth
SECRET_KEY=<a-long-random-secret>

# Required on startup (reserved for planned integrations)
QDRANT_URL=<your-qdrant-url>
QDRANT_API_KEY=<your-qdrant-api-key>
GROQ_API_KEY=<your-groq-api-key>

# Optional — email delivery (dev mode logs emails to console when unset)
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=
```

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

Chat runs against the locally fine-tuned **BioMistral-7B** model in GGUF format. The model loads once at server startup.

1. Obtain the `biomistral-Q4_K_M.gguf` file (the fine-tune pipeline is documented in [`docs/solution.md`](docs/solution.md) and [`docs/training-report.md`](docs/training-report.md)).
2. Place it anywhere on disk and point `MODEL_PATH` at it in `.env` — or put it at the default path in `app/config.py`.

---

## Project Structure

```
├── app/                      # FastAPI backend
│   ├── api/                  # Routers: auth, chat
│   ├── core/                 # LLM wrapper, security/tokens, password policy
│   ├── db/                   # Async engine + session, Base
│   ├── models/               # SQLAlchemy models (User, RefreshToken, Token)
│   ├── schemas/              # Pydantic request/response models
│   ├── services/             # Business logic (streaming chat)
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

| Method | Endpoint                 | Description                                   |
|--------|--------------------------|-----------------------------------------------|
| POST   | `/auth/register`         | Create an account (returns tokens — auto-login) |
| POST   | `/auth/login`            | Authenticate, receive access + refresh tokens |
| POST   | `/auth/refresh`          | Rotate a refresh token for a new pair         |
| GET    | `/auth/me`               | Current user profile                          |
| PATCH  | `/auth/me`               | Update profile (`full_name`, `email`)         |
| PUT    | `/auth/me/password`      | Change password (signs out all sessions)      |
| DELETE | `/auth/me`               | Delete account (requires `confirmation: "DELETE"`) |
| POST   | `/auth/forgot-password`  | Email a reset link                            |
| POST   | `/auth/reset-password`   | Complete a password reset                     |
| POST   | `/auth/send-verification`| Send an email-verification link               |
| GET    | `/auth/verify-email`     | Verify an email via one-time token            |

### Chat — `/chat`

| Method | Endpoint       | Description                                   |
|--------|----------------|-----------------------------------------------|
| POST   | `/chat/stream` | Stream a chat completion (Server-Sent tokens) |

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

Interactive API docs are available at `http://localhost:8000/docs` (Swagger UI) when the server is running.

---

## Documentation

The [`docs/`](docs/) directory contains research notes, the fine-tuning pipeline, and evaluation results:

- [`docs/solution.md`](docs/solution.md) — converting the merged fine-tuned model to GGUF
- [`docs/training-report.md`](docs/training-report.md) — QLoRA training + evaluation metrics (ROUGE, BERTScore, medical accuracy)
- [`docs/basemodel-vs-ftmodel.md`](docs/basemodel-vs-ftmodel.md) — base vs. fine-tuned comparison
- Plus weekly progress notes and the project roadmap

---

## License

All rights reserved. This project is developed for academic purposes as a final-year project.
