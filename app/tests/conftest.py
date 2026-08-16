# app/tests/conftest.py
"""Fixtures needed by tests in app/tests/.

These duplicate the root conftest fake_store because pytest.ini testpaths
only covers the root tests/ directory, so its conftest is not discovered
when running app/tests/ directly.
"""
from types import SimpleNamespace

import pytest


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
