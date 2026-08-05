# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

**Health Intelligence Companion** — a full-stack medical Q&A app with user auth. Two parts, run independently:

- **Backend** (`app/`): FastAPI + async SQLAlchemy (asyncpg → Neon Postgres), token-based auth, and local LLM inference via `llama-cpp-python` (BioMistral-7B GGUF). Serves the chat stream at `/chat/stream` and the auth API under `/auth`.
- **Frontend** (`frontend/`): React 19 + Vite 8 + Tailwind 4. Auth wire-up via localStorage JWT; chat via streaming `fetch`.

## Environment

- Backend Python runs in the **conda env `ft-project`** (`C:\miniconda3\envs\ft-project`). Dependencies are pinned in `requirements.txt` — install with `conda activate ft-project && pip install -r requirements.txt`.
- All secrets live in root `.env` (gitignored): `DATABASE_URL` (Neon/Postgres), `SECRET_KEY`, `QDRANT_URL`, `QDRANT_API_KEY`, `GROQ_API_KEY`, `HF_TOKEN`, plus dev username/password. Do **not** commit or echo these values. `app/config.py` reads them via `pydantic-settings`.

## Commands

```bash
# Backend (from repo root, conda env ft-project), port 8000
uvicorn app.main:app --reload

# Frontend (from frontend/), port 5173  — hardcoded API base http://localhost:8000
npm run dev
npm run build
npm run lint   # ESLint (frontend only)
```

There is **no backend test suite** and no backend linter configured. `app/db/session.py:init_models` creates tables directly from the SQLAlchemy models on startup via `Base.metadata.create_all` — there are **no Alembic migrations in use** (alembic is in `requirements.txt` but the code path is unused).

## Backend architecture

FastAPI app assembled in `app/main.py`: registers `auth` and `chat` routers, adds CORS (default `http://localhost:5173`), and on startup (`lifespan`) runs `validate_settings()` (requires `DATABASE_URL`, `SECRET_KEY`, `QDRANT_URL`, `GROQ_API_KEY` to be set — even though Qdrant/Groq are not yet used in code) then `await init_models()`.

Layered layout: `api/` (routers) → `schemas/` (Pydantic request/response) → `services/` (business logic) → `models/` (SQLAlchemy) + `core/` (security, password policy, LLM) + `utils/` (email, logging). `deps.py` provides auth dependencies.

### Streaming chat (the non-obvious part)

`app/core/llm.py` loads the GGUF model **at import time** (module-level `llm = Llama(model_path=settings.MODEL_PATH, n_ctx=2048)`). This is blocking and expensive — it happens when the app starts, so server startup is slow, and `llama_cpp`'s API is synchronous.

`app/services/chat_service.py:stream_chat` bridges that sync generator to async: it runs a producer in a **thread executor** (`loop.run_in_executor`) that pushes each content delta into an `asyncio.Queue` via `loop.call_soon_threadsafe`, and the async consumer yields items. Sentinels/exception objects are pushed through the same queue to signal completion/errors. Keep the blocking LLM call off the event loop — do not call `llm.create_chat_completion` directly from an async route.

### Auth & tokens

`app/core/security.py`:
- **Access tokens**: short-lived JWTs (default 15 min) carrying a `token_version` claim.
- **Opaque tokens**: refresh, password-reset, and email-verify tokens are random `secrets.token_urlsafe(48)` values; only their **SHA-256 hash** is stored in the DB (`refresh_tokens`, `tokens` tables). Verification is constant-time via `secrets.compare_digest`. Because hashes can't be reversed, refreshing/reset/verify lookups **scan all matching rows and hash-compare** (documented as intentional O(n)).
- **Revocation**: bumping a user's `token_version` (on password change/reset) invalidates all outstanding JWTs via the check in `app/deps.py:get_current_user`. Refresh tokens are rotated (marked `revoked` after use).
- Password hashing uses argon2 (`argon2-cffi`). Helper `require_role(*roles)` in `deps.py` for role-gating.

### Password policy

`app/core/password_policy.py` is the **source of truth** for password strength (length, case, digit, special char, common-password blocklist). The backend enforces it in `app/schemas/auth.py` via `model_validator` on register/reset/change schemas; the frontend `RegisterModal` mirrors these rules for UX only. Change rules here, then update the mirror.

### DB & email

- `app/db/session.py`: async engine tuned for Neon — `pool_pre_ping=True` and `pool_recycle=300` (seconds) to survive Neon's idle connection drops; `connect_args={"timeout": 60}`. Sessions via `async_sessionmaker(…, expire_on_commit=False)`.
- `app/utils/email.py`: when `SMTP_HOST` is empty (dev), emails are **logged to console** instead of sent. Set `SMTP_*` vars to activate real sending.
- `app/utils/logging_config.py`: `get_logger()` writes to console + `logs.txt`; `log_auth_event()` emits structured auth lines.

## Frontend notes

- API base is hardcoded `http://localhost:8000` in three places: `src/utils/api.js`, `src/context/AuthContext.jsx`, `src/components/ChatBox.jsx`.
- `api.js` is a thin JWT wrapper: auto-attaches `access_token` from localStorage, and on a 401 dispatches `auth:unauthorized` (listened for in `AuthContext.jsx`) to force logout.
- `AuthContext.jsx` owns auth state; any auth screen should use `useAuth()`. Access token is stored in localStorage (**not** the refresh token — refresh flow is unused on the frontend).
- `ChatBox.jsx` streams `/chat/stream` via a `ReadableStream` reader and renders assistant Markdown with a custom light renderer (code blocks, bold/italic, auto-linked URLs) — no `react-markdown` dependency.
- Tailwind 4 is wired through `@tailwindcss/vite` in `vite.config.js`.

## Docs

`docs/` holds project notes — including `solution.md` and `training-report.md` describing the fine-tuning of the base model (BioMistral-7B, QLoRA, converted to GGUF for `llama-cpp-python`) and its eval metrics. These are context around the ML pipeline, not required to run the app.