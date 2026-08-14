"""Password hashing, JWT management."""

from datetime import datetime, timedelta, timezone
from typing import Optional

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import jwt, JWTError

from app.config import settings
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

ph = PasswordHasher()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

# ======================================================================
# Password hashing
# ======================================================================


def hash_password(password: str) -> str:
    logger.debug("Hashing password")
    return ph.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        result = ph.verify(hashed, plain)
        logger.debug("Password verification succeeded")
        return result
    except VerifyMismatchError:
        logger.info("Password verification failed — mismatch")
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
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    logger.debug(
        "Access token issued | sub=%s | expires=%s | token_version=%d",
        to_encode.get("sub", "-"),
        expire.isoformat(),
        token_version,
    )
    return token


def decode_access_token(token: str) -> dict:
    """Decode a JWT.  Raises ``JWTError`` on expiry or bad signature."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        logger.debug("Token decoded | sub=%s", payload.get("sub", "-"))
        return payload
    except JWTError as e:
        logger.warning("JWT decode failed | reason=%s", e)
        raise

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_access_token(token)
        user_id: str | None = payload.get("sub")
        token_version: int | None = payload.get("token_version")
        if user_id is None:
            logger.warning("Token decoded but 'sub' claim missing")
            raise credentials_exception
    except Exception:
        logger.warning("Security get_current_user — token validation failed")
        raise credentials_exception





