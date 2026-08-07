# app/db/checkpointer.py
"""
LangGraph Postgres checkpointer — gives the agent automatic conversation
continuity. The full AgentState is persisted and reloaded per thread_id,
so prior turns' context survives without any manual DB query on our part.

Module-level singleton, loaded once at import time — same pattern as
`core/llm.py`. `.setup()` is idempotent and safe to run on every startup.
"""
from langgraph.checkpoint.postgres import PostgresSaver

from app.db.pool import build_langgraph_pool

# A pool, not a bare connection: Neon drops idle connections and the pool
# pings on checkout, reconnecting automatically (see app/db/pool.py).
checkpointer = PostgresSaver(build_langgraph_pool())
checkpointer.setup()  # creates checkpoint tables on first run, no-ops after
