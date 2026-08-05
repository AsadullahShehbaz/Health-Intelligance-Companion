"""Email sending utility.

In development mode (no SMTP configured) every outgoing email is logged
to the console instead of being sent.  Once SMTP_* vars are set in .env the
real sender activates automatically.
"""

import logging
import smtplib
import ssl
from email.message import EmailMessage
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)


def send_email(
    to: str,
    subject: str,
    body: str,
    *,
    reply_to: Optional[str] = None,
) -> bool:
    """Send an email via SMTP, or log it when SMTP is not configured.

    Returns ``True`` on success, ``False`` on failure.
    """
    if not settings.SMTP_HOST:
        logger.info(
            "[DEV email] To: %s | Subject: %s\n%s",
            to,
            subject,
            body,
        )
        return True

    msg = EmailMessage()
    msg["From"] = settings.SMTP_FROM or settings.SMTP_USER
    msg["To"] = to
    msg["Subject"] = subject
    if reply_to:
        msg["Reply-To"] = reply_to
    msg.set_content(body)

    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_TLS:
                server.starttls(context=ctx)
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        logger.info("Email sent to %s — %s", to, subject)
        return True
    except Exception:
        logger.exception("Failed to send email to %s — %s", to, subject)
        return False
