"""Unit tests for Pydantic schemas — validation errors for malformed requests."""
import pytest
from pydantic import ValidationError

from app.schemas.agent import AgentRequest, AgentResponse
from app.schemas.auth import LoginRequest, RegisterRequest
from app.schemas.chat import ChatRequest, ChatMessage


# ── RegisterRequest ──────────────────────────────────────────────────────────

@pytest.mark.unit
def test_register_valid():
    req = RegisterRequest(
        username="alice", email="alice@example.com", password="Str0ng!Pass"
    )
    assert req.username == "alice"


@pytest.mark.unit
@pytest.mark.parametrize("bad_pw", [
    "short",            # too short, missing rules
    "alllowercase1!",   # missing uppercase
    "ALLUPPERCASE1!",   # missing lowercase
    "NoDigits!!",       # missing digit
    "NoSpecial1",       # missing special char
    "password",         # common password (also short)
])
def test_register_rejects_weak_password(bad_pw):
    with pytest.raises(ValidationError) as exc:
        RegisterRequest(
            username="bob", email="bob@example.com", password=bad_pw
        )
    assert exc.value.error_count() >= 1


@pytest.mark.unit
def test_register_username_too_short():
    with pytest.raises(ValidationError):
        RegisterRequest(
            username="ab", email="ab@example.com", password="Str0ng!Pass"
        )


@pytest.mark.unit
def test_register_username_too_long():
    with pytest.raises(ValidationError):
        RegisterRequest(
            username="x" * 51, email="ab@example.com", password="Str0ng!Pass"
        )


@pytest.mark.unit
def test_register_invalid_email():
    with pytest.raises(ValidationError):
        RegisterRequest(
            username="bob", email="not-an-email", password="Str0ng!Pass"
        )


# ── LoginRequest ─────────────────────────────────────────────────────────────

@pytest.mark.unit
def test_login_valid():
    req = LoginRequest(username="alice", password="anything")
    assert req.username == "alice"


@pytest.mark.unit
def test_login_empty_username():
    with pytest.raises(ValidationError):
        LoginRequest(username="", password="x")


@pytest.mark.unit
def test_login_empty_password():
    with pytest.raises(ValidationError):
        LoginRequest(username="alice", password="")


# ── ChatMessage / ChatRequest ────────────────────────────────────────────────

@pytest.mark.unit
def test_chat_request_valid():
    req = ChatRequest(
        messages=[ChatMessage(role="user", content="hello")],
        temperature=0.5,
        max_tokens=100,
    )
    assert req.messages[0].content == "hello"


@pytest.mark.unit
def test_chat_request_invalid_role():
    with pytest.raises(ValidationError):
        ChatMessage(role="invalid_role", content="hello")


@pytest.mark.unit
def test_chat_request_empty_content():
    with pytest.raises(ValidationError):
        ChatMessage(role="user", content="")


@pytest.mark.unit
@pytest.mark.parametrize("temp", [-0.1, 2.1, 3.0])
def test_chat_request_temperature_out_of_range(temp):
    with pytest.raises(ValidationError):
        ChatRequest(
            messages=[ChatMessage(role="user", content="hi")],
            temperature=temp,
        )


@pytest.mark.unit
@pytest.mark.parametrize("tokens", [0, -1, -100])
def test_chat_request_max_tokens_must_be_positive(tokens):
    with pytest.raises(ValidationError):
        ChatRequest(
            messages=[ChatMessage(role="user", content="hi")],
            max_tokens=tokens,
        )


# ── AgentRequest / AgentResponse ─────────────────────────────────────────────

@pytest.mark.unit
def test_agent_request_defaults():
    req = AgentRequest(patient_id="p1")
    assert req.query == ""
    assert req.image_base64 is None
    assert req.thread_id is None


@pytest.mark.unit
def test_agent_request_missing_patient_id():
    with pytest.raises(ValidationError):
        AgentRequest()


@pytest.mark.unit
def test_agent_response_roundtrip():
    resp = AgentResponse(
        answer="hello",
        detected_lang="en",
        needs_rag=False,
        save_memory=False,
    )
    assert resp.sources == []
    assert resp.retrieval_decision is None
