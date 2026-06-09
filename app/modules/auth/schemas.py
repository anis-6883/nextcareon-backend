"""app/modules/auth/schemas.py - Authentication Pydantic schemas with heavy validation."""

from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.utils.validators import validate_password_strength


class StudentSignup(BaseModel):
    """Student registration schema with strong password validation."""
    full_name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    country: str = Field(default="Bangladesh", max_length=100)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return validate_password_strength(v)

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Full name cannot be empty")
        return v.strip()


class AdminSignup(BaseModel):
    """Admin registration schema."""
    full_name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return validate_password_strength(v)


class UserLogin(BaseModel):
    """User login schema."""
    email: EmailStr
    password: str = Field(min_length=1)


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"


class TokenData(BaseModel):
    """Token payload data."""
    user_id: Optional[str] = None
    role: Optional[str] = None


class RefreshToken(BaseModel):
    """Refresh token request schema."""
    refresh_token: str = Field(min_length=1)


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
