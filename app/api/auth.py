"""Auth router — Register, Login, Refresh, and Logout.

Implements a real refresh-token flow:
- Access tokens are short-lived JWTs (60 min default)
- Refresh tokens are opaque, hashed-at-rest, revocable credentials (7 days default)
- /auth/refresh exchanges a valid refresh token for a new access + refresh pair
- /auth/logout revokes the refresh token server-side
"""

from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_token,
    hash_password,
    verify_password,
)
from app.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.config import settings
from app.schemas.auth import LoginRequest, RegisterRequest, RefreshTokenRequest, TokenResponse, UserResponse
from app.utils.logging_config import log_auth_event

router = APIRouter(prefix="/auth", tags=["auth"])


async def _get_user_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def _get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()



async def _issue_token_response(db: AsyncSession, user: User) -> TokenResponse:
    """Issue a real refresh-token pair.
    
    Generates an opaque refresh token, persists its hash to the DB with an
    expiry time, and returns both the access token (JWT) and the raw refresh
    token (opaque) to the client.
    
    The refresh token is NOT persisted in plaintext — only its SHA256 hash
    is stored, so a compromised DB doesn't leak valid tokens.
    """
    access_token = create_access_token(data={"sub": str(user.id)})
    
    raw_refresh = generate_refresh_token()
    refresh_token_row = RefreshToken(
        user_id=user.id,
        token_hash=hash_token(raw_refresh),
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(refresh_token_row)
    await db.commit()
    
    return TokenResponse(access_token=access_token, refresh_token=raw_refresh)



@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    existing_username = await _get_user_by_username(db, body.username)
    existing_email = await _get_user_by_email(db, body.email)
    if existing_username or existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already taken.",
        )

    user = User(
        username=body.username,
        email=body.email,
        hashed_password=hash_password(body.password),
        full_name=body.full_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    log_auth_event("REGISTER", user.username, str(user.id), request.client.host, success=True)
    return await _issue_token_response(db, user)


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await _get_user_by_username(db, body.username)
    ip = request.client.host

    if not user or not verify_password(body.password, user.hashed_password):
        log_auth_event("LOGIN", body.username, ip=ip, success=False, detail="bad credentials")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    if not user.is_active:
        log_auth_event("LOGIN", user.username, str(user.id), ip, success=False, detail="inactive")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive.")

    log_auth_event("LOGIN", user.username, str(user.id), ip, success=True)
    return await _issue_token_response(db, user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    body: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """Exchange a valid refresh token for a new access + refresh pair.
    
    Implements token rotation: the old refresh token is revoked, preventing
    replay of a stolen token after its first use. This is the recommended
    way to invalidate tokens — far better than relying on client-side deletion
    alone.
    """
    token_hash = hash_token(body.refresh_token)
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    stored = result.scalar_one_or_none()

    # Check for invalid, revoked, or expired token
    if (
        stored is None
        or stored.revoked
        or stored.expires_at < datetime.now(timezone.utc)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    # Fetch the user to make sure they're still active
    user = await db.get(User, stored.user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    # Rotate: revoke the old token and issue a new pair.
    # This prevents replay of a stolen refresh token past its first use.
    stored.revoked = True
    await db.commit()

    logger = __import__("app.utils.logging_config", fromlist=["get_logger"]).get_logger(__name__)
    logger.info("✓ Refresh token rotated | user=%s", user.id)

    return await _issue_token_response(db, user)


@router.post("/logout")
async def logout(
    body: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """Revoke a refresh token server-side, effectively logging out the session.
    
    Unlike just deleting the frontend's local copy of the token, this actually
    invalidates the token in the DB, preventing any further use (even if the
    frontend's token is recovered or leaked).
    """
    token_hash = hash_token(body.refresh_token)
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    stored = result.scalar_one_or_none()

    if stored is None:
        # Token doesn't exist or is already revoked — that's fine, logout is idempotent
        return {"message": "Logged out"}

    # Revoke the token
    stored.revoked = True
    await db.commit()

    logger = __import__("app.utils.logging_config", fromlist=["get_logger"]).get_logger(__name__)
    logger.info("✓ User logged out | user=%s", stored.user_id)

    return {"message": "Logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user(user: User = Depends(get_current_user)):
    return user