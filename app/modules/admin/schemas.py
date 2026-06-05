"""app/modules/admin/schemas.py - Admin schemas."""

from pydantic import BaseModel, EmailStr
from enum import Enum


class Difficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class AdminLogin(BaseModel):
    email: EmailStr
    password: str


class CourseCreate(BaseModel):
    title: str
    slug: str
    description: str = ""
    difficulty: Difficulty = Difficulty.BEGINNER
    estimated_hours: int = 0