"""app/modules/skills/models.py - Skill and student skill models."""

from typing import Optional
from uuid import uuid4
from sqlmodel import SQLModel, Field, Relationship


class Skill(SQLModel, table=True):
    """Skill definition (e.g., HTML, CSS, JavaScript)."""
    __tablename__ = "skills"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    name: str = Field(max_length=100, nullable=False, unique=True)


class CourseSkill(SQLModel, table=True):
    """Skill required by a course with weight for readiness score."""
    __tablename__ = "course_skills"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    course_id: str = Field(foreign_key="courses.id", nullable=False, index=True)
    skill_id: str = Field(foreign_key="skills.id", nullable=False, index=True)
    weight: int = Field(default=1, nullable=False, gt=0)


class StudentSkill(SQLModel, table=True):
    """Student's proficiency in a skill."""
    __tablename__ = "student_skills"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    student_id: str = Field(foreign_key="students.id", nullable=False, index=True)
    skill_id: str = Field(foreign_key="skills.id", nullable=False, index=True)
    proficiency: int = Field(default=0, nullable=False, ge=0, le=100)
