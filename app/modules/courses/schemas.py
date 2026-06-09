"""app/modules/courses/schemas.py - Course, Chapter, Lesson schemas."""

from datetime import datetime
from typing import Optional, List
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
    total_xp: int
    created_at: datetime

    class Config:
        from_attributes = True


class CourseWithChapters(CourseRead):
    chapters: List["ChapterRead"] = []


class ChapterCreate(BaseModel):
    title: str = Field(max_length=255)
    order_index: int = Field(gt=0)
    xp_reward: int = Field(default=0)
    coin_reward: int = Field(default=0)


class ChapterRead(BaseModel):
    id: str
    course_id: str
    title: str
    order_index: int
    xp_reward: int
    coin_reward: int

    class Config:
        from_attributes = True


class ChapterWithLessons(ChapterRead):
    lessons: List["LessonRead"] = []


class LessonCreate(BaseModel):
    title: str = Field(max_length=255)
    content_text: str = Field(default="")
    image_url: Optional[str] = Field(default=None, max_length=500)
    code_example: Optional[str] = Field(default=None)
    order_index: int = Field(gt=0)


class LessonRead(BaseModel):
    id: str
    chapter_id: str
    title: str
    content_text: str
    image_url: Optional[str]
    code_example: Optional[str]
    tts_audio_url: Optional[str]
    order_index: int

    class Config:
        from_attributes = True


class LessonComplete(BaseModel):
    lesson_id: str
    completed_at: Optional[datetime] = None
