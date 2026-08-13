# app/db/lifespan.py
"""
LangGraph Postgres backends, owned by the FastAPI lifespan.

Both the checkpointer (conversation continuity) and the store (per-patient
fact/emotion memory) are module-level singletons built on the shared Neon
psycopg pool (`app/db/pool.py`), so graph compilation at import time and
`conversation_service`'s queries both see ready objects without blocking
on the DB (pool construction is non-blocking — connections open on a
background worker).

`.setup()` is deferred from import time into the lifespan start: table
creation happens once per server start (idempotent, no-ops after the first
run), and the pools are closed on shutdown.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore

from app.db.pool import build_langgraph_pool

_checkpointer_pool = build_langgraph_pool()
checkpointer = PostgresSaver(_checkpointer_pool)

_store_pool = build_langgraph_pool()
store = PostgresStore(_store_pool)


@asynccontextmanager
async def lifespan(app: FastAPI):
    checkpointer.setup()  # creates checkpoint tables on first run, no-ops after
    store.setup()         # creates store tables on first run, no-ops after
    try:
        yield
    finally:
        _checkpointer_pool.close()
        _store_pool.close()