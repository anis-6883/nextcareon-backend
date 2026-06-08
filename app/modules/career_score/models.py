"""app/modules/career_score/models.py - Career score and progress models."""

from datetime import datetime
from typing import Optional, List
from uuid import uuid4
from sqlmodel import SQLModel, Field, Relationship
import enum


class MetricType(str, enum.Enum):
    """Metric types for score overrides."""
    COURSE_COMPLETION = "COURSE_COMPLETION"
    QUIZ = "QUIZ"
    PROJECT = "PROJECT"
    PORTFOLIO = "PORTFOLIO"
    INTERVIEW = "INTERVIEW"
    TOTAL = "TOTAL"


class CareerScore(SQLModel, table=True):
    """Student career score with weighted components."""
    __tablename__ = "career_scores"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    student_id: str = Field(foreign_key="students.id", nullable=False, unique=True, index=True)
    course_completion_score: float = Field(default=0.0, nullable=False, ge=0, le=100)
    quiz_performance_score: float = Field(default=0.0, nullable=False, ge=0, le=100)
    project_quality_score: float = Field(default=0.0, nullable=False, ge=0, le=100)
    portfolio_strength_score: float = Field(default=0.0, nullable=False, ge=0, le=100)
    mock_interview_score: float = Field(default=0.0, nullable=False, ge=0, le=100)
    total_career_score: float = Field(default=0.0, nullable=False, ge=0, le=100, index=True)
    last_calculated_at: Optional[datetime] = Field(default=None, nullable=True)

    student: Optional["Student"] = Relationship(back_populates="career_score")
    history: List["CareerScoreHistory"] = Relationship(
        back_populates="student",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )


class CareerScoreHistory(SQLModel, table=True):
    """Historical record of career score changes."""
    __tablename__ = "career_score_history"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    student_id: str = Field(foreign_key="students.id", nullable=False, index=True)
    total_career_score: float = Field(nullable=False, ge=0, le=100)
    recorded_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    student: Optional["Student"] = Relationship()


class AdminScoreOverrideAuditLog(SQLModel, table=True):
    """Audit log for admin score overrides."""
    __tablename__ = "admin_score_override_audit_log"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    student_id: str = Field(foreign_key="students.id", nullable=False, index=True)
    admin_id: str = Field(foreign_key="admin_users.id", nullable=False, index=True)
    metric_changed: MetricType = Field(nullable=False)
    old_value: float = Field(nullable=False)
    new_value: float = Field(nullable=False)
    reason_for_override: str = Field(default="", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    student: Optional["Student"] = Relationship()
    admin: Optional["AdminUser"] = Relationship()


class MockInterviewCredit(SQLModel, table=True):
    """Mock interview credits for students."""
    __tablename__ = "mock_interview_credits"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    student_id: str = Field(foreign_key="students.id", nullable=False, unique=True, index=True)
    available_credits: int = Field(default=0, nullable=False, ge=0)
    total_purchased_or_earned: int = Field(default=0, nullable=False, ge=0)

    student: Optional["Student"] = Relationship(back_populates="mock_interview_credits")


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

    student: Optional["Student"] = Relationship()
    course: Optional["Course"] = Relationship()


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


from app.modules.users.models import Student
from app.modules.courses.models import Course, Chapter