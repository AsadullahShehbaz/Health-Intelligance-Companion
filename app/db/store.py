# app/db/store.py
"""
LangGraph Postgres store — persisted key/value memory, namespaced per
patient. Facts are stored under ("patient_facts", patient_id) so they can
be queried independently of any conversation, which is what makes a fact
like "fever a week ago" survive across many unrelated turns.

Module-level singleton, loaded once at import time — same pattern as
`core/llm.py`. `.setup()` is idempotent and safe to run on every startup.
"""
from langgraph.store.postgres import PostgresStore

from app.db.pool import build_langgraph_pool

# A pool, not a bare connection: Neon drops idle connections and the pool
# pings on checkout, reconnecting automatically (see app/db/pool.py).
store = PostgresStore(build_langgraph_pool())
store.setup()  # creates store tables on first run, no-ops after
