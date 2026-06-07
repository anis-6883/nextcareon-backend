"""app/modules/career_paths/models.py - Career path and related models."""

from datetime import datetime
from typing import Optional, List
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

    courses: List["CareerPathCourse"] = Relationship(
        back_populates="career_path",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )
    enrollments: List["StudentCareerPath"] = Relationship(
        back_populates="career_path",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )
    market_data: Optional["CareerPathMarketData"] = Relationship(
        back_populates="career_path",
        sa_relationship_kwargs={"lazy": "selectin"}
    )
    job_openings: List["JobOpening"] = Relationship(
        back_populates="career_path",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )
    alumni_showcase: List["AlumniShowcase"] = Relationship(
        back_populates="career_path",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )


class CareerPathCourse(SQLModel, table=True):
    """Links a course to a career path (M2M relationship)."""
    __tablename__ = "career_path_courses"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    career_path_id: str = Field(foreign_key="career_paths.id", nullable=False, index=True)
    course_id: str = Field(foreign_key="courses.id", nullable=False, index=True)
    order_index: int = Field(nullable=False)

    career_path: Optional[CareerPath] = Relationship(back_populates="courses")


class StudentCareerPath(SQLModel, table=True):
    """Student enrollment in a career path."""
    __tablename__ = "student_career_paths"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    student_id: str = Field(foreign_key="students.id", nullable=False, index=True)
    career_path_id: str = Field(foreign_key="career_paths.id", nullable=False, index=True)
    status: CareerPathStatus = Field(default=CareerPathStatus.ENROLLED, nullable=False)
    enrolled_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    student: Optional["Student"] = Relationship(back_populates="career_enrollments")
    career_path: Optional[CareerPath] = Relationship(back_populates="enrollments")


class Company(SQLModel, table=True):
    """Company model for market intelligence."""
    __tablename__ = "companies"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    name: str = Field(max_length=255, nullable=False, unique=True, index=True)
    logo_url: Optional[str] = Field(default=None, max_length=500)
    description: str = Field(default="", nullable=False)
    is_active: bool = Field(default=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    job_openings: List["JobOpening"] = Relationship(
        back_populates="company",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )


class SalaryRange(SQLModel, table=True):
    """Salary range linked to a career path with localization."""
    __tablename__ = "salary_ranges"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    career_path_id: str = Field(foreign_key="career_paths.id", nullable=False, unique=True, index=True)
    country: str = Field(max_length=100, nullable=False)
    min_salary: int = Field(nullable=False)
    max_salary: int = Field(nullable=False)
    avg_salary: int = Field(nullable=False)
    currency: str = Field(default="USD", max_length=3, nullable=False)

    career_path: Optional[CareerPath] = Relationship()


class JobOpening(SQLModel, table=True):
    """Job opening for a career path."""
    __tablename__ = "job_openings"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    career_path_id: str = Field(foreign_key="career_paths.id", nullable=False, index=True)
    company_id: str = Field(foreign_key="companies.id", nullable=False, index=True)
    title: str = Field(max_length=255, nullable=False)
    location: str = Field(max_length=255, nullable=False)
    application_url: str = Field(max_length=500, nullable=False)
    description: str = Field(default="", nullable=False)
    is_active: bool = Field(default=True, nullable=False)
    posted_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    career_path: Optional[CareerPath] = Relationship(back_populates="job_openings")
    company: Optional[Company] = Relationship(back_populates="job_openings")


class AlumniShowcase(SQLModel, table=True):
    """Alumni showcase for career paths."""
    __tablename__ = "alumni_showcase"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    career_path_id: str = Field(foreign_key="career_paths.id", nullable=False, index=True)
    student_id: Optional[str] = Field(default=None, foreign_key="students.id", nullable=True, index=True)
    name: str = Field(max_length=255, nullable=False)
    current_job_title: str = Field(max_length=255, nullable=False)
    company_name: str = Field(max_length=255, nullable=False)
    linkedin_url: Optional[str] = Field(default=None, max_length=500)
    story: str = Field(default="", nullable=False)
    is_featured: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    career_path: Optional[CareerPath] = Relationship(back_populates="alumni_showcase")


class CareerPathMarketData(SQLModel, table=True):
    """Market intelligence for a career path."""
    __tablename__ = "career_path_market_data"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    career_path_id: str = Field(foreign_key="career_paths.id", nullable=False, unique=True, index=True)
    job_market_summary: str = Field(default="", nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    career_path: Optional[CareerPath] = Relationship(back_populates="market_data")