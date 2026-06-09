"""app/modules/admin/schemas.py - Admin schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.utils.validators import validate_password_strength


class Difficulty(str):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class AdminLogin(BaseModel):
    email: EmailStr
    password: str


class CourseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=255)
    description: str = ""
    difficulty: str = "beginner"
    estimated_hours: int = 0


class StudentRead(BaseModel):
    """Student public profile for admin view."""
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


class StudentUpdate(BaseModel):
    """Schema for updating student by admin."""
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=255)
    country: Optional[str] = Field(default=None, max_length=100)
    education_level: Optional[str] = Field(default=None, max_length=100)
    experience_level: Optional[str] = Field(default=None, max_length=100)
    dream_career: Optional[str] = Field(default=None, max_length=255)


class AdminUserRead(BaseModel):
    """Admin user profile for admin view."""
    id: str
    full_name: str
    email: EmailStr
    role: str
    created_at: datetime


class AdminUserCreate(BaseModel):
    """Schema for creating admin user with strong password validation."""
    full_name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    role: str = "content_manager"

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        return validate_password_strength(v)
