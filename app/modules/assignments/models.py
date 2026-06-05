"""app/modules/assignments/models.py - Assignment and Project models."""

from datetime import datetime
from typing import Optional, List
from uuid import uuid4
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum


class SubmissionStatus(str, Enum):
    """Submission status."""
    SUBMITTED = "submitted"
    GRADED = "graded"


class Assignment(SQLModel, table=True):
    """Assignment model - course requirement."""
    __tablename__ = "assignments"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    course_id: str = Field(foreign_key="courses.id", nullable=False, index=True)
    title: str = Field(max_length=255, nullable=False)
    description: str = Field(default="", nullable=False)
    xp_reward: int = Field(default=50, nullable=False)
    coin_reward: int = Field(default=100, nullable=False)

    # Relationships
    course: Optional["Course"] = Relationship(back_populates="assignments")
    submissions: List["StudentAssignmentSubmission"] = Relationship(back_populates="assignment", sa_relationship_kwargs={"lazy": "selectin"})


class Project(SQLModel, table=True):
    """Final project model."""
    __tablename__ = "projects"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    course_id: str = Field(foreign_key="courses.id", nullable=False, index=True)
    title: str = Field(max_length=255, nullable=False)
    description: str = Field(default="", nullable=False)
    requirements_url: Optional[str] = Field(default=None, max_length=500)
    xp_reward: int = Field(default=100, nullable=False)
    coin_reward: int = Field(default=300, nullable=False)

    # Relationships
    course: Optional["Course"] = Relationship(back_populates="projects")
    submissions: List["StudentProjectSubmission"] = Relationship(back_populates="project", sa_relationship_kwargs={"lazy": "selectin"})


class StudentAssignmentSubmission(SQLModel, table=True):
    """Student assignment submission."""
    __tablename__ = "student_assignment_submissions"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    student_id: str = Field(foreign_key="students.id", nullable=False, index=True)
    assignment_id: str = Field(foreign_key="assignments.id", nullable=False, index=True)
    submission_url: str = Field(max_length=500, nullable=False)
    status: SubmissionStatus = Field(default=SubmissionStatus.SUBMITTED, nullable=False)
    score: Optional[int] = Field(default=None, ge=0, le=100)
    submitted_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    student: Optional["Student"] = Relationship(back_populates="assignment_submissions")
    assignment: Optional[Assignment] = Relationship(back_populates="submissions")


class StudentProjectSubmission(SQLModel, table=True):
    """Student project submission."""
    __tablename__ = "student_project_submissions"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    student_id: str = Field(foreign_key="students.id", nullable=False, index=True)
    project_id: str = Field(foreign_key="projects.id", nullable=False, index=True)
    submission_url: str = Field(max_length=500, nullable=False)
    status: SubmissionStatus = Field(default=SubmissionStatus.SUBMITTED, nullable=False)
    score: Optional[int] = Field(default=None, ge=0, le=100)
    feedback: Optional[str] = Field(default=None)
    submitted_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    student: Optional["Student"] = Relationship(back_populates="project_submissions")
    project: Optional[Project] = Relationship(back_populates="submissions")


# Forward references
from app.modules.courses.models import Course
from app.modules.users.models import Student