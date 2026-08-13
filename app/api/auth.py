"""Auth router — simplified to Register + Login (Phase 5).

Forgot/reset password, change password, delete account, email verification,
and token refresh were all removed to keep the project focused on chat
history. If the React frontend still calls those endpoints, those calls
will 404 until the frontend is updated to match.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, get_current_user, hash_password, verify_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.utils.logging_config import log_auth_event

router = APIRouter(prefix="/auth", tags=["auth"])


async def _get_user_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def _get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


def _issue_token_response(user: User) -> TokenResponse:
    """Build the response the React client expects.

    session.js stores both access_token and refresh_token — but the
    refresh-token table/rotation flow is gone in Phase 5, so refresh_token
    here is just a copy of access_token, not a real second credential.
    """
    access_token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(access_token=access_token, refresh_token=access_token)


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
    return _issue_token_response(user)


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
    return _issue_token_response(user)

@router.get("/me")
async def get_current_user(user: User = Depends(get_current_user)):
    return user    