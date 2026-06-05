"""app/modules/career_score/models.py - Career score and progress models."""

from datetime import datetime
from typing import Optional
from uuid import uuid4
from sqlmodel import SQLModel, Field, Relationship


class StudentCourseProgress(SQLModel, table=True):
    """Tracks student enrollment and progress in a course."""
    __tablename__ = "student_course_progress"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    student_id: str = Field(foreign_key="students.id", nullable=False, index=True)
    course_id: str = Field(foreign_key="courses.id", nullable=False, index=True)
    completion_pct: int = Field(default=0, nullable=False, ge=0, le=100)
    status: str = Field(default="enrolled", nullable=False)
    enrolled_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    completed_at: Optional[datetime] = Field(default=None)


class StudentChapterProgress(SQLModel, table=True):
    """Tracks student chapter completion."""
    __tablename__ = "student_chapter_progress"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    student_id: str = Field(foreign_key="students.id", nullable=False, index=True)
    chapter_id: str = Field(foreign_key="chapters.id", nullable=False, index=True)
    is_completed: bool = Field(default=False, nullable=False)
    completed_at: Optional[datetime] = Field(default=None)


class MockInterviewSession(SQLModel, table=True):
    """Mock interview conducted for a student."""
    __tablename__ = "mock_interview_sessions"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    student_id: str = Field(foreign_key="students.id", nullable=False, index=True)
    score_percent: int = Field(default=0, nullable=False, ge=0, le=100)
    feedback: str = Field(default="", nullable=False)
    conducted_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)