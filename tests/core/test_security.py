"""Unit tests for app/core/security.py — password hashing, JWT creation/decoding."""
import time
from datetime import timedelta

import pytest
from jose import JWTError

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


# ── Password hashing ─────────────────────────────────────────────────────────

@pytest.mark.unit
def test_hash_password_returns_different_hash():
    h = hash_password("TestPass123!")
    assert h != "TestPass123!"
    assert len(h) > 20


@pytest.mark.unit
def test_verify_password_correct():
    h = hash_password("MySecret1!")
    assert verify_password("MySecret1!", h) is True


@pytest.mark.unit
def test_verify_password_wrong():
    h = hash_password("MySecret1!")
    assert verify_password("wrong", h) is False


@pytest.mark.unit
def test_verify_password_empty():
    h = hash_password("MySecret1!")
    assert verify_password("", h) is False


# ── JWT creation / decoding ───────────────────────────────────────────────────

@pytest.mark.unit
def test_create_and_decode_token_roundtrip():
    token = create_access_token(data={"sub": "user-abc"})
    payload = decode_access_token(token)
    assert payload["sub"] == "user-abc"
    assert payload["token_version"] == 1  # default


@pytest.mark.unit
def test_token_includes_expiry():
    token = create_access_token(data={"sub": "x"})
    payload = decode_access_token(token)
    assert "exp" in payload


@pytest.mark.unit
def test_token_version_claim():
    token = create_access_token(data={"sub": "x"}, token_version=3)
    payload = decode_access_token(token)
    assert payload["token_version"] == 3


@pytest.mark.unit
def test_custom_expiry():
    token = create_access_token(
        data={"sub": "x"},
        expires_delta=timedelta(seconds=1),
    )
    payload = decode_access_token(token)
    assert "exp" in payload
    # Should be ~1 second from now
    assert abs(payload["exp"] - time.time()) < 5


@pytest.mark.unit
def test_decode_invalid_token_raises():
    with pytest.raises(JWTError):
        decode_access_token("not.a.valid.token")


@pytest.mark.unit
def test_decode_tampered_token_raises():
    token = create_access_token(data={"sub": "x"})
    # Truncate the signature — always invalid
    with pytest.raises(JWTError):
        decode_access_token(token[:-5] + "XXXXX")
