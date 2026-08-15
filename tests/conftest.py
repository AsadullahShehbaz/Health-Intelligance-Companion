"""Root conftest — loaded before any test module.

This file is the single point of control that makes the entire test suite
dependency-free:

1.  Sets dummy env vars BEFORE any ``app.*`` import so ``Settings()`` doesn't
    crash on missing required fields.
2.  Stubs ``sentence_transformers`` in ``sys.modules`` so that
    ``qdrant_store.py``'s module-level ``get_embedder()`` call doesn't
    download a ~90 MB model at import time.
3.  Monkey-patches ``build_langgraph_pool`` to return a ``MagicMock`` so
    ``db/lifespan.py``'s module-level pool construction doesn't start
    background threads that try to connect to a non-existent Postgres.
"""
import os
import sys
import types
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
import pytest_asyncio

# ═══════════════════════════════════════════════════════════════════════════
# 1. DUMMY ENV VARS — must be set before any `from app.config import settings`
# ═══════════════════════════════════════════════════════════════════════════
_DUMMY_ENV = {
    "DATABASE_URL": "postgresql+asyncpg://test:test@localhost/testdb",
    "QDRANT_URL": "http://localhost:6333",
    "QDRANT_API_KEY": "test-qdrant-key",
    "HF_TOKEN": "test-hf-token",
    "SECRET_KEY": "test-secret-key-for-jwt-signing-32chars",
    "SERP_API_KEY": "test-serp-key",
    "GROQ_API_KEY": "test-groq-key",
}
for _k, _v in _DUMMY_ENV.items():
    os.environ.setdefault(_k, _v)

# ═══════════════════════════════════════════════════════════════════════════
# 2. STUB sentence_transformers
#    qdrant_store.py calls `embedder = get_embedder()` at module level, which
#    would load a real SentenceTransformer model. Replace with a fake.
# ═══════════════════════════════════════════════════════════════════════════
if not getattr(sys.modules.get("sentence_transformers"), "_is_test_stub", False):
    import numpy as np

    _fake_st = types.ModuleType("sentence_transformers")
    _fake_st._is_test_stub = True

    class _FakeSentenceTransformer:
        """Returns deterministic 384-dim zero vectors — no model download."""

        def __init__(self, *args, **kwargs):
            pass

        def encode(self, text, **kwargs):
            return np.zeros(384)

        def embed_query(self, text):
            return np.zeros(384).tolist()

    _fake_st.SentenceTransformer = _FakeSentenceTransformer
    sys.modules["sentence_transformers"] = _fake_st

# ═══════════════════════════════════════════════════════════════════════════
# 3. PREVENT POOL BACKGROUND THREADS
#    db/lifespan.py calls `build_langgraph_pool()` at module level, which
#    creates a real psycopg ConnectionPool that starts a background worker
#    thread trying to connect to Postgres. Replace with a MagicMock so no
#    threads are spawned and no connection attempts are made.
# ═══════════════════════════════════════════════════════════════════════════
import app.db.pool  # noqa: E402 — safe: pure string computation, no I/O
app.db.pool.build_langgraph_pool = lambda: MagicMock()  # type: ignore[assignment]


# ═══════════════════════════════════════════════════════════════════════════
# 4. FAKE LLM
# ═══════════════════════════════════════════════════════════════════════════

class FakeLLM:
    """Deterministic fake LLM for unit tests.

    Configure per-test by setting attributes on the returned instance::

        fake_llm.response_text = "Custom answer"
        fake_llm.tool_calls   = [{"name": "retrieve_medical_knowledge", "args": {"query": "..."}, "id": "..."}]
        fake_llm.stream_chunks = ["Hello", " world"]
        fake_llm.should_error = True   # to test error / sentinel paths
    """

    def __init__(self):
        self.response_text = "Test response from fake LLM."
        self.tool_calls: list | None = None
        self.stream_chunks = ["Hello", " ", "world"]
        self.should_error = False

    async def astream(self, messages, **kwargs):
        if self.should_error:
            raise RuntimeError("Fake LLM error")
        for chunk_text in self.stream_chunks:
            yield SimpleNamespace(content=chunk_text)

    def bind_tools(self, tools):
        # Return self so .invoke() works the same way whether or not tools
        # are bound — both the router and biomistral nodes call
        # `model.invoke(messages)` uniformly.
        return self

    def invoke(self, messages):
        if self.should_error:
            raise RuntimeError("Fake LLM error")
        from langchain_core.messages import AIMessage

        return AIMessage(
            content=self.response_text,
            tool_calls=self.tool_calls or [],
        )


# ═══════════════════════════════════════════════════════════════════════════
# 5. SKIP live MARKER UNLESS RUN_LIVE_TESTS=1
# ═══════════════════════════════════════════════════════════════════════════

def pytest_collection_modifyitems(config, items):
    """Skip @pytest.mark.live tests unless RUN_LIVE_TESTS=1."""
    if os.environ.get("RUN_LIVE_TESTS") == "1":
        return
    skip_live = pytest.mark.skip(reason="Set RUN_LIVE_TESTS=1 to run live tests")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip_live)


# ═══════════════════════════════════════════════════════════════════════════
# 6. FIXTURES
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def fake_llm(monkeypatch):
    """Replace the LLM singletons with a deterministic fake in every module
    that holds one — both the BioMistral node (``llm``) and the router node
    (``router_llm``, a ChatGroq bound with tools)."""
    import importlib

    fake = FakeLLM()
    for mod_path in [
        "app.core.llm",
        "app.services.chat_service",
        "app.services.rag_chat_service",
        "app.agent.nodes.biomistral_node",
    ]:
        mod = importlib.import_module(mod_path)
        monkeypatch.setattr(mod, "llm", fake)

    # The router uses its own bound ChatGroq instance — swap it for the fake
    # so .invoke() runs without a real Groq call.
    router_mod = importlib.import_module("app.agent.nodes.router_node")
    monkeypatch.setattr(router_mod, "router_llm", fake)
    return fake


@pytest.fixture
def fake_qdrant(monkeypatch):
    """Stub Qdrant ``retrieve`` (as imported in corrective_rag) to return
    canned high-relevance docs."""

    def _fake_retrieve(query, top_k=5, category=None):
        return [
            {"text": "Diabetes is a chronic condition.", "source": "who.int",
             "category": "endocrine", "score": 0.85},
            {"text": "Symptoms include excessive thirst.", "source": "mayoclinic.org",
             "category": "endocrine", "score": 0.72},
        ]

    monkeypatch.setattr("app.core.rag.corrective_rag.retrieve", _fake_retrieve)
    return _fake_retrieve


@pytest.fixture
def fake_serpapi(monkeypatch):
    """Stub SerpAPI ``GoogleSearch`` to avoid real API calls."""

    class _FakeGoogleSearch:
        def __init__(self, params):
            self.params = params

        def get_dict(self):
            return {
                "organic_results": [
                    {"snippet": "Web result snippet", "link": "example.com",
                     "title": "Example"},
                ]
            }

    monkeypatch.setattr("app.core.rag.corrective_rag.GoogleSearch", _FakeGoogleSearch)
    return _FakeGoogleSearch


# ── DB fixtures ─────────────────────────────────────────────────────────────

@pytest_asyncio.fixture(scope="session")
async def db_engine():
    """Session-scoped in-memory sqlite engine with all tables created.

    Uses ``StaticPool`` so all sessions share a single in-memory connection
    (aiosqlite in-memory DBs are per-connection by default — without
    StaticPool each session would get its own empty database).  Tables are
    created once per session and data is truncated per-test in ``db_session``.
    """
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy.pool import StaticPool
    from app.db.base import Base
    import app.models  # noqa: F401 — registers User/Token/RefreshToken

    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    """Per-test async DB session that truncates all tables on teardown."""
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
    from app.db.base import Base

    session_maker = async_sessionmaker(
        db_engine, expire_on_commit=False, class_=AsyncSession
    )
    async with session_maker() as session:
        yield session
        # Truncate every table so the next test starts with a clean slate.
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        await session.commit()


# ── ASGI client ──────────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def async_client(db_engine):
    """``httpx.AsyncClient`` over the FastAPI app.

    The lifespan is NOT triggered (ASGITransport sends only ``http.request``
    events, not ``lifespan.startup``), so no real Postgres/Qdrant/LLM
    connections are made on startup.  ``get_db`` is overridden to use the
    test sqlite engine.
    """
    from httpx import AsyncClient, ASGITransport
    from app.main import app
    from app.db.session import get_db
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

    session_maker = async_sessionmaker(
        db_engine, expire_on_commit=False, class_=AsyncSession
    )

    async def get_test_db():
        async with session_maker() as session:
            yield session

    app.dependency_overrides[get_db] = get_test_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


# ── Auth helpers ─────────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def auth_user(db_session):
    """Create a test user in the DB and return it."""
    import uuid
    from app.core.security import hash_password
    from app.models.user import User

    user = User(
        id=uuid.uuid4(),
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("TestPass123!"),
        role="user",
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def auth_token(auth_user):
    """JWT for the test user."""
    from app.core.security import create_access_token
    return create_access_token(data={"sub": str(auth_user.id)})


@pytest.fixture
def auth_headers(auth_token):
    """Authorization headers for the test user."""
    return {"Authorization": f"Bearer {auth_token}"}


# ── Agent helpers ────────────────────────────────────────────────────────────

@pytest.fixture
def fake_store():
    """In-memory fake of the LangGraph ``PostgresStore`` for tools tests."""

    class _FakeStore:
        def __init__(self):
            self._data: dict[tuple, dict[str, dict]] = {}

        def get(self, namespace, key):
            ns = tuple(namespace)
            value = self._data.get(ns, {}).get(key)
            if value is None:
                return None
            return SimpleNamespace(key=key, value=value)

        def search(self, namespace, query="", limit=5):
            ns = tuple(namespace)
            items = [
                SimpleNamespace(value=v)
                for v in self._data.get(ns, {}).values()
            ]
            return items[:limit]

        def put(self, namespace, key, value):
            ns = tuple(namespace)
            self._data.setdefault(ns, {})[key] = value

    return _FakeStore()


@pytest.fixture
def sample_state():
    """Factory for ``AgentState`` dicts — accepts overrides."""

    def _make(**kwargs):
        base = {
            "patient_id": "test-patient-01",
            "ocr_context": "",
            "tool_results": "",
            "messages": [],
            "answer": "",
            "final_response": "",
            "raw_input": "What is diabetes?",
            "detected_lang": "en",
            "needs_rag": False,
            "retrieval_decision": "",
            "retrieved_docs": [],
            "saved_memory": False,
            "remembered_context": "",
        }
        base.update(kwargs)
        return base

    return _make
