from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, model_validator

from app.core.password_policy import validate_password

# =========================================================================
# Request Schemas
# =========================================================================


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)  # actual length checked in validator
    full_name: Optional[str] = Field(None, max_length=100)

    @model_validator(mode="after")
    def _check_password_policy(self):
        errors = validate_password(self.password)
        if errors:
            raise ValueError(
                "; ".join(e.message for e in errors)
            )
        return self


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# =========================================================================
# Response Schemas
# =========================================================================


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    full_name: Optional[str] = None
    role: str
    is_active: bool
    is_verified: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    message: str
