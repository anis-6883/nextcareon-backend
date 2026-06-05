"""app/modules/career_paths/models.py - Career path and related models."""

from datetime import datetime
from typing import Optional
from uuid import uuid4
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum


class CareerPathDifficulty(str, Enum):
    """Career path difficulty."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class CareerPathStatus(str, Enum):
    """Student career path enrollment status."""
    ENROLLED = "enrolled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class CareerPath(SQLModel, table=True):
    """Career path - groups courses for a career goal."""
    __tablename__ = "career_paths"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    title: str = Field(max_length=255, nullable=False)
    slug: str = Field(max_length=255, nullable=False, unique=True, index=True)
    description: str = Field(default="", nullable=False)
    difficulty: CareerPathDifficulty = Field(default=CareerPathDifficulty.MEDIUM, nullable=False)
    estimated_hours: int = Field(default=0, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class CareerPathCourse(SQLModel, table=True):
    """Links a course to a career path."""
    __tablename__ = "career_path_courses"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    career_path_id: str = Field(foreign_key="career_paths.id", nullable=False, index=True)
    course_id: str = Field(foreign_key="courses.id", nullable=False, index=True)
    order_index: int = Field(nullable=False)


class StudentCareerPath(SQLModel, table=True):
    """Student enrollment in a career path."""
    __tablename__ = "student_career_paths"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    student_id: str = Field(foreign_key="students.id", nullable=False, index=True)
    career_path_id: str = Field(foreign_key="career_paths.id", nullable=False, index=True)
    completion_pct: int = Field(default=0, nullable=False, ge=0, le=100)
    status: CareerPathStatus = Field(default=CareerPathStatus.ENROLLED, nullable=False)
    readiness_score: int = Field(default=0, nullable=False, ge=0, le=100)
    enrolled_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class CareerPathMarketData(SQLModel, table=True):
    """Market intelligence for a career path."""
    __tablename__ = "career_path_market_data"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    career_path_id: str = Field(foreign_key="career_paths.id", nullable=False, unique=True, index=True)
    salary_range: str = Field(max_length=255, nullable=False)
    job_market_summary: str = Field(default="", nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class CareerPathCompany(SQLModel, table=True):
    """Companies hiring for this career path."""
    __tablename__ = "career_path_companies"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    career_path_id: str = Field(foreign_key="career_paths.id", nullable=False, index=True)
    company_name: str = Field(max_length=255, nullable=False)
    logo_url: Optional[str] = Field(default=None, max_length=500)
    hiring_status: str = Field(default="active", max_length=100)


class CareerPathJobOpening(SQLModel, table=True):
    """Job openings for this career path."""
    __tablename__ = "career_path_job_openings"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    career_path_id: str = Field(foreign_key="career_paths.id", nullable=False, index=True)
    title: str = Field(max_length=255, nullable=False)
    company_name: str = Field(max_length=255, nullable=False)
    location: str = Field(max_length=255, nullable=False)
    url: str = Field(max_length=500, nullable=False)
    posted_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class CareerPathAlumni(SQLModel, table=True):
    """Alumni featured for this career path."""
    __tablename__ = "career_path_alumni"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    career_path_id: str = Field(foreign_key="career_paths.id", nullable=False, index=True)
    student_id: Optional[str] = Field(default=None, foreign_key="students.id", nullable=True, index=True)
    current_job_title: str = Field(max_length=255, nullable=False)
    company_name: str = Field(max_length=255, nullable=False)
    linkedin_url: Optional[str] = Field(default=None, max_length=500)