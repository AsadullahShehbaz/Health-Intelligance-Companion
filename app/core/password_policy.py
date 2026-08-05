"""Password strength policy shared between backend and frontend docs.

Rules here are enforced server-side. The frontend RegisterModal mirrors them
for a snappy UX, but the server is the source of truth.
"""

import re

# ── Policy constants (exported so frontend docs can reference them) ────────

MIN_LENGTH = 8
MAX_LENGTH = 128
MIN_LOWERCASE = 1
MIN_UPPERCASE = 1
MIN_DIGIT = 1
MIN_SPECIAL = 1

# Common / known-bad passwords that should always be rejected
COMMON_PASSWORDS: set[str] = {
    "password", "password1", "password123",
    "12345678", "123456789", "1234567890",
    "qwerty123", "qwertyuiop",
    "letmein", "welcome", "monkey", "dragon",
    "abc123", "abc1234", "abc12345",
    "P@ssw0rd", "Passw0rd", "passw0rd",
}


# ── Validation ────────────────────────────────────────────────────────────

class PasswordError:
    """Describes a single password policy violation."""
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message

    def __repr__(self) -> str:
        return f"PasswordError({self.code}: {self.message})"


def validate_password(password: str) -> list[PasswordError]:
    """Return a list of policy violations (empty = valid)."""
    errors: list[PasswordError] = []

    if len(password) < MIN_LENGTH:
        errors.append(PasswordError(
            "too_short",
            f"Password must be at least {MIN_LENGTH} characters.",
        ))
    if len(password) > MAX_LENGTH:
        errors.append(PasswordError(
            "too_long",
            f"Password must be at most {MAX_LENGTH} characters.",
        ))
    if MIN_UPPERCASE and sum(1 for c in password if c.isupper()) < MIN_UPPERCASE:
        errors.append(PasswordError(
            "missing_uppercase",
            f"Password must contain at least {MIN_UPPERCASE} uppercase letter.",
        ))
    if MIN_LOWERCASE and sum(1 for c in password if c.islower()) < MIN_LOWERCASE:
        errors.append(PasswordError(
            "missing_lowercase",
            f"Password must contain at least {MIN_LOWERCASE} lowercase letter.",
        ))
    if MIN_DIGIT and sum(1 for c in password if c.isdigit()) < MIN_DIGIT:
        errors.append(PasswordError(
            "missing_digit",
            f"Password must contain at least {MIN_DIGIT} digit.",
        ))
    if MIN_SPECIAL and sum(1 for c in password if not c.isalnum()) < MIN_SPECIAL:
        errors.append(PasswordError(
            "missing_special",
            f"Password must contain at least {MIN_SPECIAL} special character.",
        ))
    if password.lower() in COMMON_PASSWORDS:
        errors.append(PasswordError(
            "common_password",
            "This password is too common. Choose a more unique one.",
        ))

    return errors
