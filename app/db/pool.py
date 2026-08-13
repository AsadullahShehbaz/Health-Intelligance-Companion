# app/db/pool.py
"""
Shared psycopg ConnectionPool for the LangGraph checkpointer and store.

Both langgraph postgres backends take either a bare psycopg connection or a
psycopg_pool pool. A bare connection is a live grenade against Neon:
serverless autosuspend drops idle connections, and with no reconnect path
the first request after idle dies with

    psycopg.OperationalError: SSL connection has been closed unexpectedly

and stays dead — psycopg marks the closed connection unusable, so every
subsequent request fails the same way.

A pool fixes it the way the async engine's `pool_pre_ping=True` does: the
pool's default `check` runs a no-op statement on every checkout, so a stale
connection is discarded and replaced before it is used.

`autocommit`/`prepare_threshold`/`row_factory` mirror what langgraph's
`from_conn_string` passes to `Connection.connect` — the saver/store rely on
those being set. `connect_timeout` and keepalives match the Neon tuning in
`app/db/session.py`.

The LangGraph connections deliberately use Neon's **direct endpoint**, not
the `-pooler` (PgBouncer transaction-mode) one that `DATABASE_URL` points at.
The checkpointer/store hold long-lived connections and rely on server-side
prepared statements (`prepare_threshold=0`) and binary cursors — a
transaction-mode pooler is not designed for that and aborts such connections
(`could not receive data from server: Software caused connection abort`).
The direct endpoint gives real sessions, which is what langgraph's code
expects; the pool handles the remaining autosuspend drops.
"""
from urllib.parse import urlparse, urlunparse

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.config import settings


def _langgraph_conn_string() -> str:
    """DATABASE_URL for the LangGraph psycopg connections.

    Two adjustments on top of the asyncpg URL:
      1. psycopg dialect instead of asyncpg's.
      2. Use Neon's *direct* endpoint (host without ``-pooler.``) rather than
         the PgBouncer pooler endpoint — see module docstring. No-op when the
         host isn't a Neon pooler host.
    """
    u = urlparse(settings.DATABASE_URL.replace("postgresql+asyncpg", "postgresql"))
    host = u.hostname or ""
    if "-pooler." in host:
        userinfo = ""
        if u.username:
            userinfo = u.username + (f":{u.password}" if u.password else "") + "@"
        netloc = userinfo + host.replace("-pooler.", ".")
        if u.port:
            netloc += f":{u.port}"
        u = u._replace(netloc=netloc)
    return urlunparse(u)


_conn_string = _langgraph_conn_string()


def build_langgraph_pool() -> ConnectionPool:
    """A process-lifetime pool tuned for Neon serverless Postgres.

    Non-blocking to construct: the pool opens its connections on a
    background worker, so module import never waits on the DB.
    """
    return ConnectionPool(
        conninfo=_conn_string,
        kwargs={
            # Same non-negotiables as langgraph's own from_conn_string().
            "autocommit": True,
            "prepare_threshold": 0,
            "row_factory": dict_row,
            # Neon can take several seconds to wake a suspended compute.
            "connect_timeout": 60,
            # Detect server-side drops (Neon idle timeout) faster.
            "keepalives": 1,
            "keepalives_idle": 60,
            "keepalives_interval": 15,
            "keepalives_count": 3,
        },
        # psycopg_pool's default checkout timeout (30s) is shorter than the
        # per-connect timeout above, so the first checkout during a slow Neon
        # wake would fail before the connect does. Let a checkout wait out the
        # full wake instead of giving up early.
        timeout=90,
        min_size=1,
        max_size=5,
        # Recycle proactively rather than reuse a long-stale pooled conn.
        max_lifetime=900,
        max_idle=300,
    )
