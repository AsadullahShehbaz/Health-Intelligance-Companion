# File: app/db/pool.py
import time

import psycopg
from psycopg_pool import ConnectionPool

from app.config import settings
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

# Neon autosuspends an idle compute and kills its connections. The pool
# reconnects on checkout, but the *first* query on a fresh connection can
# still abort while the compute is waking — add the same single retry used
# elsewhere for transient DB blips.
_MAX_DB_RETRIES = 1
_RETRY_DELAY_SECONDS = 0.5


def run_with_retry(fn, *args, max_retries: int = _MAX_DB_RETRIES, delay: float = _RETRY_DELAY_SECONDS, **kwargs):
    for attempt in range(max_retries + 1):
        try:
            return fn(*args, **kwargs)
        except psycopg.OperationalError:
            if attempt >= max_retries:
                raise
            logger.warning(
                "Transient DB error in memory operation (attempt %d/%d), retrying...",
                attempt + 1,
                max_retries + 1,
            )
            time.sleep(delay)


# Convert async/sync SQLAlchemy direct Neon URL to raw psycopg format
def get_psycopg_conn_string() -> str:
    conn_str = settings.DATABASE_URL
    # Replace asyncpg / postgresql+asyncpg schemes if present
    conn_str = conn_str.replace("postgresql+asyncpg://", "postgres://")
    conn_str = conn_str.replace("postgresql://", "postgres://")
    return conn_str


def build_langgraph_pool() -> ConnectionPool:
    conn_str = get_psycopg_conn_string()
    logger.info("Building resilient psycopg ConnectionPool for Neon DB")

    return ConnectionPool(
        conninfo=conn_str,
        min_size=1,
        max_size=10,
        timeout=30.0,            # Wait up to 30s for a connection checkout
        max_lifetime=300.0,       # Recycle connections every 5 mins to stay ahead of Neon idle timeout
        max_idle=60.0,            # Close idle connections after 60s
        reconnect_timeout=30.0,   # Automatically retry reconnecting if Neon is resuming
        kwargs={
            "autocommit": True,
            "prepare_threshold": 0,
            "connect_timeout": 15,
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 5,
        },
    )