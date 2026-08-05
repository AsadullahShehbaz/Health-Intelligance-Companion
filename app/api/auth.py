"""Auth router — register, login, refresh, profile, password reset, email verify."""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.security import (
    create_access_token,
    decode_access_token,
    generate_opaque_token,
    hash_password,
    verify_opaque_token,
    verify_password,
)
from app.db.session import get_db
from app.deps import get_current_user
from app.models.refresh_token import RefreshToken
from app.models.token import Token as OneTimeToken
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    DeleteAccountRequest,
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UpdateProfileRequest,
    UserResponse,
)
from app.utils.email import send_email
from app.utils.logging_config import log_auth_event

router = APIRouter(prefix="/auth", tags=["auth"])


# ── Helpers ──────────────────────────────────────────────────────────────────


async def _get_user_by_username(
    db: AsyncSession, username: str
) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def _get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def _issue_tokens(
    db: AsyncSession, user: User, ip: str | None = None
) -> dict:
    """Create an access-token JWT + opaque refresh token, persist the refresh."""
    access_token = create_access_token(
        data={"sub": str(user.id)},
        token_version=user.token_version,
    )

    raw_refresh, refresh_hash = generate_opaque_token()
    refresh_expires = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=refresh_hash,
            expires_at=refresh_expires,
        )
    )
    await db.commit()

    log_auth_event("LOGIN", user.username, str(user.id), ip, success=True)
    return {
        "access_token": access_token,
        "refresh_token": raw_refresh,
    }


# ── Register ─────────────────────────────────────────────────────────────────


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    body: RegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user account.

    Returns an access + refresh token pair (auto-login) so the user doesn't
    need to sign in immediately after creating an account.
    """
    # Check uniqueness with a single generic error to prevent enumeration
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

    tokens = await _issue_tokens(db, user, request.client.host)

    log_auth_event(
        "REGISTER", user.username, str(user.id), request.client.host, success=True
    )
    return TokenResponse(**tokens)


# ── Login ────────────────────────────────────────────────────────────────────


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate with username + password, receive access + refresh tokens."""
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
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive.",
        )

    tokens = await _issue_tokens(db, user, ip)
    return TokenResponse(**tokens)


# ── Refresh token ────────────────────────────────────────────────────────────


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    body: RefreshTokenRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Exchange a valid refresh token for a new access + refresh token pair."""
    ip = request.client.host

    # Find the matching refresh token by iterating active ones (hash comparison)
    # This is intentionally O(n) on active refresh tokens — the alternative
    # would be storing a hash we can't reverse, so we scan.
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.revoked == False,  # noqa: E712
            RefreshToken.expires_at > now,
        )
    )
    stored = result.scalars().all()

    matched: RefreshToken | None = None
    for rt in stored:
        if verify_opaque_token(body.refresh_token, rt.token_hash):
            matched = rt
            break

    if not matched:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
        )

    # Revoke the used refresh token (rotation)
    matched.revoked = True

    # Fetch the user and issue a fresh pair
    user_result = await db.execute(select(User).where(User.id == matched.user_id))
    user = user_result.scalar_one_or_none()

    if not user or not user.is_active:
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account not found or inactive.",
        )

    tokens = await _issue_tokens(db, user, ip)
    await db.commit()

    return TokenResponse(**tokens)


# ── Me — read ────────────────────────────────────────────────────────────────


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user's profile."""
    return current_user


# ── Me — update profile ─────────────────────────────────────────────────────


@router.patch("/me", response_model=UserResponse)
async def update_profile(
    body: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update profile fields (full_name, email)."""
    if body.full_name is not None:
        current_user.full_name = body.full_name
    if body.email is not None:
        # Check email uniqueness
        existing = await _get_user_by_email(db, body.email)
        if existing and existing.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already in use.",
            )
        current_user.email = body.email

    await db.commit()
    await db.refresh(current_user)
    return current_user


# ── Me — change password ────────────────────────────────────────────────────


@router.put("/me/password", response_model=MessageResponse)
async def change_password(
    body: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Change the current user's password.  Increments token_version to
    invalidate all existing sessions."""
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect.",
        )

    current_user.hashed_password = hash_password(body.new_password)
    current_user.token_version += 1  # invalidates existing JWTs
    await db.commit()

    log_auth_event(
        "PASSWORD_CHANGE",
        current_user.username,
        str(current_user.id),
        detail="token_version bumped",
    )
    return MessageResponse(message="Password changed. All active sessions have been signed out.")


# ── Me — delete account ─────────────────────────────────────────────────────


@router.delete("/me", response_model=MessageResponse)
async def delete_account(
    body: DeleteAccountRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Permanently delete the authenticated user's account."""
    if body.confirmation != "DELETE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Send confirmation: 'DELETE' as the confirmation field.",
        )
    if not verify_password(body.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password is incorrect.",
        )

    await db.delete(current_user)
    await db.commit()

    log_auth_event(
        "ACCOUNT_DELETED",
        current_user.username,
        str(current_user.id),
    )
    return MessageResponse(message="Account permanently deleted.")


# ── Password reset: forgot ──────────────────────────────────────────────────


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    body: ForgotPasswordRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Send a password-reset email (or log it in dev)."""
    user = await _get_user_by_email(db, body.email)
    # Always return OK to prevent email enumeration
    ip = request.client.host

    if user:
        raw, token_hash = generate_opaque_token()
        expires = datetime.now(timezone.utc) + timedelta(
            hours=settings.RESET_TOKEN_EXPIRE_HOURS
        )
        db.add(
            OneTimeToken(
                user_id=user.id,
                purpose="reset",
                token_hash=token_hash,
                expires_at=expires,
            )
        )
        await db.commit()

        reset_link = f"{settings.CORS_ORIGINS[0]}/reset-password?token={raw}"
        send_email(
            to=user.email,
            subject="Password Reset — Health Intelligence",
            body=(
                f"Hi {user.username},\n\n"
                f"Click the link below to reset your password:\n{reset_link}\n\n"
                f"This link expires in {settings.RESET_TOKEN_EXPIRE_HOURS} hour(s).\n"
                "If you didn't request this, ignore this email."
            ),
        )
        log_auth_event(
            "PASSWORD_RESET_REQUESTED",
            user.username,
            str(user.id),
            ip,
            success=True,
        )

    return MessageResponse(
        message="If an account with that email exists, a reset link has been sent."
    )


# ── Password reset: reset ───────────────────────────────────────────────────


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    body: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """Complete a password reset using the token from the email."""
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(OneTimeToken).where(
            OneTimeToken.purpose == "reset",
            OneTimeToken.used == False,  # noqa: E712
            OneTimeToken.expires_at > now,
        )
    )
    stored_tokens = result.scalars().all()

    matched: OneTimeToken | None = None
    for t in stored_tokens:
        if verify_opaque_token(body.token, t.token_hash):
            matched = t
            break

    if not matched:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token.",
        )

    # Mark token as used
    matched.used = True

    # Update password + bump token_version to invalidate all sessions
    user_result = await db.execute(select(User).where(User.id == matched.user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    user.hashed_password = hash_password(body.new_password)
    user.token_version += 1
    await db.commit()

    log_auth_event(
        "PASSWORD_RESET_COMPLETED",
        user.username,
        str(user.id),
        detail="token_version bumped",
    )
    return MessageResponse(message="Password reset successfully. You can now sign in.")


# ── Email verification ──────────────────────────────────────────────────────


@router.post("/send-verification", response_model=MessageResponse)
async def send_verification_email(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send an email-verification link."""

    if current_user.is_verified:
        return MessageResponse(message="Email already verified.")

    raw, token_hash = generate_opaque_token()
    expires = datetime.now(timezone.utc) + timedelta(
        hours=settings.VERIFY_TOKEN_EXPIRE_HOURS
    )
    db.add(
        OneTimeToken(
            user_id=current_user.id,
            purpose="verify",
            token_hash=token_hash,
            expires_at=expires,
        )
    )
    await db.commit()

    verify_link = (
        f"{settings.CORS_ORIGINS[0]}/verify-email?token={raw}"
    )
    send_email(
        to=current_user.email,
        subject="Verify your email — Health Intelligence",
        body=(
            f"Hi {current_user.username},\n\n"
            f"Click the link below to verify your email:\n{verify_link}\n\n"
            f"This link expires in {settings.VERIFY_TOKEN_EXPIRE_HOURS} hour(s)."
        ),
    )

    log_auth_event(
        "VERIFICATION_EMAIL_SENT",
        current_user.username,
        str(current_user.id),
        success=True,
    )
    return MessageResponse(message="Verification email sent.")


@router.get("/verify-email", response_model=MessageResponse)
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    """Verify a user's email address using a one-time token."""
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(OneTimeToken).where(
            OneTimeToken.purpose == "verify",
            OneTimeToken.used == False,  # noqa: E712
            OneTimeToken.expires_at > now,
        )
    )
    stored_tokens = result.scalars().all()

    matched: OneTimeToken | None = None
    for t in stored_tokens:
        if verify_opaque_token(token, t.token_hash):
            matched = t
            break

    if not matched:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token.",
        )

    matched.used = True
    user_result = await db.execute(select(User).where(User.id == matched.user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    user.is_verified = True
    await db.commit()

    log_auth_event(
        "EMAIL_VERIFIED",
        user.username,
        str(user.id),
        success=True,
    )
    return MessageResponse(message="Email verified successfully.")
