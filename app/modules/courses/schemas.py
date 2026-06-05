"""app/modules/courses/schemas.py - Course schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CourseCreate(BaseModel):
    title: str = Field(max_length=255)
    slug: str = Field(max_length=255)
    description: str = Field(default="")
    difficulty: str = Field(default="beginner")
    estimated_hours: int = Field(default=0)


class CourseRead(BaseModel):
    id: str
    title: str
    slug: str
    description: str
    difficulty: str
    estimated_hours: int
    created_at: datetime


class ChapterRead(BaseModel):
    id: str
    course_id: str
    title: str
    order_index: int


class LessonRead(BaseModel):
    id: str
    chapter_id: str
    title: str
    order_index: int