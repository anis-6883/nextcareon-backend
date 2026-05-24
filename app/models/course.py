from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.career_path import CareerPath


class Course(SQLModel, table=True):
    """
    Course model for curriculum content management.
    Represents a structured learning course that can contain multiple skills and projects.
    """

    __tablename__ = "course"

    # ── Primary Key ──────────────────────────────────────────
    course_id: Optional[int] = Field(default=None, primary_key=True)

    # ── Course Identity ───────────────────────────────────────
    title: str = Field(max_length=200, nullable=False, unique=True, index=True)
    description: str = Field(max_length=2000, nullable=False)
    code: Optional[str] = Field(
        default=None,
        max_length=50,
        nullable=True,
        unique=True,
        index=True,
        description="Course code (e.g., 'CSE101', 'WEB201')"
    )

    # ── Career Path Association ───────────────────────────────
    path_id: Optional[int] = Field(
        default=None,
        foreign_key="career_path.path_id",
        nullable=True,
        index=True,
        description="Optional link to a career path"
    )

    # ── Course Structure ──────────────────────────────────────
    level_required: int = Field(default=1, nullable=False, description="Minimum user level to access")
    level_unlocked: int = Field(default=1, nullable=False, description="User level at which course unlocks")
    duration_weeks: int = Field(default=4, nullable=False, description="Expected course duration in weeks")
    xp_reward: int = Field(default=100, nullable=False, description="XP awarded on course completion")

    # ── Status & Metadata ─────────────────────────────────────
    status: str = Field(
        default="published",
        max_length=20,
        nullable=False,
        description="'draft', 'published', 'archived'"
    )
    is_active: bool = Field(default=True, nullable=False, description="Whether course is available")
    difficulty: str = Field(
        default="intermediate",
        max_length=20,
        description="'beginner', 'intermediate', 'advanced', 'expert'"
    )

    # ── Syllabus & Content ────────────────────────────────────
    syllabus: Optional[str] = Field(
        default=None,
        max_length=5000,
        nullable=True,
        description="Detailed course syllabus/outline"
    )
    learning_outcomes: Optional[str] = Field(
        default=None,
        max_length=2000,
        nullable=True,
        description="JSON array of learning outcomes"
    )

    # ── Assessment ────────────────────────────────────────────
    has_quiz: bool = Field(default=True, nullable=False, description="Whether course includes quiz")
    quiz_passing_score: int = Field(default=70, nullable=False, description="Required percentage to pass")
    has_certification: bool = Field(default=False, nullable=False, description="Whether course offers certification")

    # ── Timestamps ────────────────────────────────────────────
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    published_at: Optional[datetime] = Field(default=None, nullable=True)

    # ── Relationships ─────────────────────────────────────────
    career_path: Optional["CareerPath"] = Relationship(back_populates="courses")
