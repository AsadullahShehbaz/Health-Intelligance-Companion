"""Password hashing, JWT management, and opaque-token generation."""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import JWTError, jwt

from app.config import settings

ph = PasswordHasher()

# ======================================================================
# Password hashing
# ======================================================================


def hash_password(password: str) -> str:
    return ph.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return ph.verify(hashed, plain)
    except VerifyMismatchError:
        return False


# ======================================================================
# Access tokens (JWT — short-lived, includes token_version)
# ======================================================================


def create_access_token(
    data: dict,
    *,
    token_version: int = 1,
    expires_delta: Optional[timedelta] = None,
) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "token_version": token_version})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Decode a JWT.  Raises ``JWTError`` on expiry or bad signature."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


# ======================================================================
# Opaque tokens (refresh, password-reset, email-verify)
# Stored as SHA-256 hashes so a DB leak doesn't expose live tokens.
# ======================================================================


def _hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


def generate_opaque_token() -> tuple[str, str]:
    """Return ``(raw_token, sha256_hash)``.

    Give the raw token to the client; store the hash in the database.
    """
    raw = secrets.token_urlsafe(48)
    return raw, _hash_token(raw)


def verify_opaque_token(raw: str, stored_hash: str) -> bool:
    """Constant-time comparison of a raw token against its stored hash."""
    return secrets.compare_digest(_hash_token(raw), stored_hash)
