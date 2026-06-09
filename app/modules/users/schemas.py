"""app/modules/users/schemas.py - Pydantic schemas for user auth."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.utils.validators import validate_password_strength


class StudentSignup(BaseModel):
    """Student registration schema with strong password validation."""
    full_name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    country: str = Field(default="Bangladesh", max_length=100)
    education_level: Optional[str] = Field(default=None, max_length=100)
    experience_level: Optional[str] = Field(default=None, max_length=100)
    dream_career: Optional[str] = Field(default=None, max_length=255)

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


class StudentRead(BaseModel):
    """Student public profile."""
    id: str
    full_name: str
    email: EmailStr
    country: str
    education_level: Optional[str] = None
    experience_level: Optional[str] = None
    dream_career: Optional[str] = None
    xp_points: int
    level: int
    coins: int
    daily_streak: int
    created_at: datetime


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data."""
    user_id: Optional[str] = None
    role: Optional[str] = None


class UserLogin(BaseModel):
    """User login schema."""
    email: EmailStr
    password: str
