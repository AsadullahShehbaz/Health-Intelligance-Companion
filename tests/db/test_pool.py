"""Unit tests for app/db/pool.py — connection-string rewriting pure function.

``_langgraph_conn_string`` rewrites the DATABASE_URL in two ways:
  1. ``postgresql+asyncpg`` → ``postgresql`` (psycopg dialect)
  2. Neon ``-pooler.`` host → direct host (strip ``-pooler.``)

Both are pure string operations — no DB connection needed.
"""
import pytest

from app.db.pool import _langgraph_conn_string


# ── asyncpg → psycopg dialect ────────────────────────────────────────────────

@pytest.mark.unit
def test_rewrites_asyncpg_to_psycopg(monkeypatch):
    monkeypatch.setattr(
        "app.db.pool.settings.DATABASE_URL",
        "postgresql+asyncpg://user:pass@db.example.com/mydb",
    )
    result = _langgraph_conn_string()
    assert result.startswith("postgresql://")
    assert "asyncpg" not in result


# ── pooler → direct host ──────────────────────────────────────────────────────

@pytest.mark.unit
def test_strips_pooler_from_neon_host(monkeypatch):
    monkeypatch.setattr(
        "app.db.pool.settings.DATABASE_URL",
        "postgresql+asyncpg://user:pass@ep-cool-name-pooler.us-east-2.aws.neon.tech/db",
    )
    result = _langgraph_conn_string()
    # -pooler. should become . so the host is the direct endpoint
    assert "-pooler." not in result
    assert "ep-cool-name.us-east-2.aws.neon.tech" in result


@pytest.mark.unit
def test_preserves_credentials_when_stripping_pooler(monkeypatch):
    monkeypatch.setattr(
        "app.db.pool.settings.DATABASE_URL",
        "postgresql+asyncpg://alice:s3cr3t@ep-cool-name-pooler.us-east-2.aws.neon.tech/db",
    )
    result = _langgraph_conn_string()
    assert "alice:s3cr3t@" in result


@pytest.mark.unit
def test_preserves_port_when_stripping_pooler(monkeypatch):
    monkeypatch.setattr(
        "app.db.pool.settings.DATABASE_URL",
        "postgresql+asyncpg://u:p@ep-cool-pooler.us-east-2.aws.neon.tech:5432/db",
    )
    result = _langgraph_conn_string()
    assert ":5432" in result


# ── no-op when host isn't a pooler host ───────────────────────────────────────

@pytest.mark.unit
def test_noop_when_not_pooler_host(monkeypatch):
    direct = "postgresql+asyncpg://user:pass@db.example.com:5432/mydb"
    monkeypatch.setattr("app.db.pool.settings.DATABASE_URL", direct)
    result = _langgraph_conn_string()
    # Only the dialect should change; the host stays the same.
    assert "db.example.com" in result
    assert "-pooler." not in result


@pytest.mark.unit
def test_noop_when_already_postgresql(monkeypatch):
    """If the URL is already `postgresql://` it should be returned as-is."""
    monkeypatch.setattr(
        "app.db.pool.settings.DATABASE_URL",
        "postgresql://user:pass@db.example.com/mydb",
    )
    result = _langgraph_conn_string()
    assert result == "postgresql://user:pass@db.example.com/mydb"
