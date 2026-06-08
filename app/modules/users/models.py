"""app/modules/users/models.py - Student and Admin user models."""

from datetime import datetime
from typing import Optional, List
from uuid import uuid4
from sqlmodel import SQLModel, Field, Relationship
import enum


class UserRole(str, enum.Enum):
    """Admin user roles."""
    SUPER_ADMIN = "super_admin"
    CONTENT_MANAGER = "content_manager"
    MODERATOR = "moderator"


class EducationLevel(str, enum.Enum):
    """Student education levels."""
    HIGH_SCHOOL = "high_school"
    BACHELOR = "bachelor"
    MASTER = "master"
    PHD = "phd"
    OTHER = "other"


class ExperienceLevel(str, enum.Enum):
    """Student experience levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Student(SQLModel, table=True):
    """Student model - core user for the platform."""
    __tablename__ = "students"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    full_name: str = Field(max_length=255, nullable=False)
    email: str = Field(max_length=255, nullable=False, unique=True, index=True)
    password_hash: str = Field(max_length=255, nullable=False)
    country: str = Field(default="Bangladesh", max_length=100, nullable=False)
    education_level: Optional[EducationLevel] = Field(default=None, nullable=True)
    experience_level: Optional[ExperienceLevel] = Field(default=None, nullable=True)
    dream_career: Optional[str] = Field(default=None, max_length=255)
    xp_points: int = Field(default=0, nullable=False)
    level: int = Field(default=1, nullable=False)
    coins: int = Field(default=0, nullable=False)
    daily_streak: int = Field(default=0, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    enrollments: List["Enrollment"] = Relationship(
        back_populates="student",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )
    career_enrollments: List["StudentCareerPath"] = Relationship(
        back_populates="student",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )
    lesson_progress: List["LessonProgress"] = Relationship(
        back_populates="student",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )
    quiz_attempts: List["QuizAttempt"] = Relationship(
        back_populates="student",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )
    assignment_submissions: List["StudentAssignmentSubmission"] = Relationship(
        back_populates="student",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )
    project_submissions: List["StudentProjectSubmission"] = Relationship(
        back_populates="student",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )
    career_score: Optional["CareerScore"] = Relationship(
        back_populates="student",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )
    mock_interview_credits: Optional["MockInterviewCredit"] = Relationship(
        back_populates="student",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )
    coin_ledger: List["CoinLedger"] = Relationship(
        back_populates="student",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )
    balance: Optional["UserBalance"] = Relationship(
        back_populates="student",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )
    achievements: List["UserAchievement"] = Relationship(
        back_populates="student",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )
    inventory: List["StudentInventory"] = Relationship(
        back_populates="student",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )
    ai_credit_gate: Optional["AiCreditGate"] = Relationship(
        back_populates="student",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )


from app.modules.courses.models import (
    Enrollment, LessonProgress, QuizAttempt,
    StudentAssignmentSubmission, StudentProjectSubmission
)
from app.modules.career_paths.models import StudentCareerPath
from app.modules.career_score.models import CareerScore, MockInterviewCredit
from app.modules.gamification.models import (
    CoinLedger, UserBalance, UserAchievement, StudentInventory, AiCreditGate
)


class AdminUser(SQLModel, table=True):
    """Admin user for platform management."""
    __tablename__ = "admin_users"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    full_name: str = Field(max_length=255, nullable=False)
    email: str = Field(max_length=255, nullable=False, unique=True, index=True)
    password_hash: str = Field(max_length=255, nullable=False)
    role: UserRole = Field(default=UserRole.CONTENT_MANAGER, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)