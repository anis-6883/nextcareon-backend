"""app/modules/courses/models.py - Course, Chapter, Lesson models."""

from datetime import datetime
from typing import Optional, List
from uuid import uuid4
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Enum
import enum


class Difficulty(str, enum.Enum):
    """Course difficulty levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Course(SQLModel, table=True):
    """Course model."""
    __tablename__ = "courses"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    title: str = Field(max_length=255, nullable=False)
    slug: str = Field(max_length=255, nullable=False, unique=True, index=True)
    description: str = Field(default="", nullable=False)
    thumbnail_url: Optional[str] = Field(default=None, max_length=500)
    difficulty: Difficulty = Field(default=Difficulty.BEGINNER, nullable=False)
    estimated_hours: int = Field(default=0, nullable=False)
    total_xp: int = Field(default=0, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class Chapter(SQLModel, table=True):
    """Chapter model - groups lessons and contains a quiz."""
    __tablename__ = "chapters"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    course_id: str = Field(foreign_key="courses.id", nullable=False, index=True)
    title: str = Field(max_length=255, nullable=False)
    order_index: int = Field(nullable=False)
    xp_reward: int = Field(default=0, nullable=False)
    coin_reward: int = Field(default=0, nullable=False)


class Lesson(SQLModel, table=True):
    """Lesson model - text content with optional media."""
    __tablename__ = "lessons"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    chapter_id: str = Field(foreign_key="chapters.id", nullable=False, index=True)
    title: str = Field(max_length=255, nullable=False)
    content_text: str = Field(default="", nullable=False)
    image_url: Optional[str] = Field(default=None, max_length=500)
    code_example: Optional[str] = Field(default=None)
    tts_audio_url: Optional[str] = Field(default=None, max_length=500)
    order_index: int = Field(nullable=False)