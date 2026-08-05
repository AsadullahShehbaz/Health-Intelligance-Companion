"""Logging configuration with structured auth-event support."""

import logging
import sys
from typing import Optional


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    logger.setLevel(logging.INFO)

    if not logger.handlers:  # prevents duplicate logs on reload
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%H:%M:%S",
        )

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        logger.addHandler(console_handler)

        file_handler = logging.FileHandler("logs.txt", mode="a", encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)

    return logger


# Pre-built loggers for core subsystems
auth_logger = get_logger("auth")


def log_auth_event(
    event: str,
    username: Optional[str] = None,
    user_id: Optional[str] = None,
    ip: Optional[str] = None,
    success: bool = True,
    detail: Optional[str] = None,
) -> None:
    """Emit a structured auth event log line.

    Example output::

        14:30:01  | INFO     | auth | LOGIN  alice@example.com 200 192.168.1.1
        14:30:02  | WARNING  | auth | LOGIN  alice@example.com 401 192.168.1.1 "bad password"
    """
    status = "OK" if success else "FAIL"
    parts = [event.upper(), username or "-", status]
    if ip:
        parts.append(ip)
    if detail:
        parts.append(repr(detail))

    msg = "  ".join(parts)
    if success:
        auth_logger.info(msg)
    else:
        auth_logger.warning(msg)
