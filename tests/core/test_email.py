"""Unit tests for app/utils/email.py — dev-mode logging + SMTP path."""
import pytest

from app.utils.email import send_email


@pytest.mark.unit
def test_send_email_dev_mode_returns_true(monkeypatch):
    """When SMTP_HOST is empty, email is logged to console and returns True."""
    monkeypatch.setattr("app.utils.email.settings.SMTP_HOST", "")
    assert send_email("user@example.com", "Test", "Body text") is True


@pytest.mark.unit
def test_send_email_smtp_success(monkeypatch):
    """When SMTP is configured, sends via smtplib and returns True."""
    monkeypatch.setattr("app.utils.email.settings.SMTP_HOST", "smtp.example.com")
    monkeypatch.setattr("app.utils.email.settings.SMTP_PORT", 587)
    monkeypatch.setattr("app.utils.email.settings.SMTP_TLS", True)
    monkeypatch.setattr("app.utils.email.settings.SMTP_USER", "user")
    monkeypatch.setattr("app.utils.email.settings.SMTP_PASSWORD", "pass")
    monkeypatch.setattr("app.utils.email.settings.SMTP_FROM", "from@example.com")

    sent = {}

    class _FakeSMTP:
        def __init__(self, host, port):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *a):
            return False
        def starttls(self, context=None):
            pass
        def login(self, user, pw):
            pass
        def send_message(self, msg):
            sent["subject"] = msg["Subject"]
            sent["to"] = msg["To"]

    monkeypatch.setattr("app.utils.email.smtplib.SMTP", _FakeSMTP)
    assert send_email("to@example.com", "Hello", "Body") is True
    assert sent["subject"] == "Hello"
    assert sent["to"] == "to@example.com"


@pytest.mark.unit
def test_send_email_smtp_failure_returns_false(monkeypatch):
    """When SMTP sending fails, returns False (not raises)."""
    monkeypatch.setattr("app.utils.email.settings.SMTP_HOST", "smtp.example.com")
    monkeypatch.setattr("app.utils.email.settings.SMTP_PORT", 587)
    monkeypatch.setattr("app.utils.email.settings.SMTP_TLS", False)
    monkeypatch.setattr("app.utils.email.settings.SMTP_USER", "")
    monkeypatch.setattr("app.utils.email.settings.SMTP_PASSWORD", "")

    class _BoomSMTP:
        def __init__(self, host, port):
            raise ConnectionRefusedError("no SMTP")

    monkeypatch.setattr("app.utils.email.smtplib.SMTP", _BoomSMTP)
    assert send_email("to@example.com", "Subject", "Body") is False


@pytest.mark.unit
def test_send_email_with_reply_to(monkeypatch):
    """reply_to adds a Reply-To header."""
    monkeypatch.setattr("app.utils.email.settings.SMTP_HOST", "")

    # In dev mode, just verify it doesn't crash and returns True
    assert send_email(
        "to@example.com", "Sub", "Body",
        reply_to="reply@example.com",
    ) is True
