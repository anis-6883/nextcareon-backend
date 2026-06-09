"""app/modules/courses/models.py - Course, Chapter, Lesson models."""

from datetime import datetime
from typing import Optional, List
from uuid import uuid4
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Enum, ForeignKey
import enum


class Difficulty(str, enum.Enum):
    """Course difficulty levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Course(SQLModel, table=True):
    """Course model."""
    __tablename__ = "courses"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    title: str = Field(max_length=255, nullable=False)
    slug: str = Field(max_length=255, nullable=False, unique=True, index=True)
    description: str = Field(default="", nullable=False)
    thumbnail_url: Optional[str] = Field(default=None, max_length=500)
    difficulty: Difficulty = Field(default=Difficulty.BEGINNER, nullable=False)
    estimated_hours: int = Field(default=0, nullable=False)
    total_xp: int = Field(default=0, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    chapters: List["Chapter"] = Relationship(
        back_populates="course",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )
    lessons: List["Lesson"] = Relationship(
        back_populates="course",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )
    quizzes: List["Quiz"] = Relationship(
        back_populates="course",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )
    assignments: List["Assignment"] = Relationship(
        back_populates="course",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )
    projects: List["Project"] = Relationship(
        back_populates="course",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )
    enrollments: List["Enrollment"] = Relationship(
        back_populates="course",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )


class Chapter(SQLModel, table=True):
    """Chapter model - groups lessons and contains a quiz."""
    __tablename__ = "chapters"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    course_id: str = Field(ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    title: str = Field(max_length=255, nullable=False)
    order_index: int = Field(nullable=False)
    xp_reward: int = Field(default=0, nullable=False)
    coin_reward: int = Field(default=0, nullable=False)

    course: Optional[Course] = Relationship(back_populates="chapters")
    lessons: List["Lesson"] = Relationship(
        back_populates="chapter",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )
    quiz: Optional["Quiz"] = Relationship(
        back_populates="chapter",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )


class Lesson(SQLModel, table=True):
    """Lesson model - text content with optional media."""
    __tablename__ = "lessons"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    course_id: str = Field(ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    chapter_id: str = Field(ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False, index=True)
    title: str = Field(max_length=255, nullable=False)
    content_text: str = Field(default="", nullable=False)
    image_url: Optional[str] = Field(default=None, max_length=500)
    code_example: Optional[str] = Field(default=None)
    tts_audio_url: Optional[str] = Field(default=None, max_length=500)
    order_index: int = Field(nullable=False)

    course: Optional[Course] = Relationship(back_populates="lessons")
    chapter: Optional[Chapter] = Relationship(back_populates="lessons")
    progress_records: List["LessonProgress"] = Relationship(
        back_populates="lesson",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )


class Quiz(SQLModel, table=True):
    """Quiz model - one per chapter."""
    __tablename__ = "quizzes"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    course_id: str = Field(ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    chapter_id: str = Field(ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    pass_score: int = Field(default=60, nullable=False, ge=0, le=100)
    xp_reward: int = Field(default=100, nullable=False)
    coin_reward: int = Field(default=25, nullable=False)

    course: Optional[Course] = Relationship(back_populates="quizzes")
    chapter: Optional[Chapter] = Relationship(back_populates="quiz")
    questions: List["Question"] = Relationship(
        back_populates="quiz",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )
    attempts: List["QuizAttempt"] = Relationship(
        back_populates="quiz",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )


class Question(SQLModel, table=True):
    """Quiz question with 4 options."""
    __tablename__ = "quiz_questions"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    quiz_id: str = Field(ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False, index=True)
    question_text: str = Field(nullable=False)
    option_a: str = Field(max_length=500, nullable=False)
    option_b: str = Field(max_length=500, nullable=False)
    option_c: str = Field(max_length=500, nullable=False)
    option_d: str = Field(max_length=500, nullable=False)
    correct_option: str = Field(max_length=1, nullable=False)

    quiz: Optional[Quiz] = Relationship(back_populates="questions")


class QuizAttempt(SQLModel, table=True):
    """Student quiz attempt."""
    __tablename__ = "quiz_attempts"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    student_id: str = Field(ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    quiz_id: str = Field(ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False, index=True)
    score: int = Field(ge=0, le=100, nullable=False)
    passed: bool = Field(nullable=False)
    attempt_number: int = Field(default=1, nullable=False)
    attempted_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    quiz: Optional[Quiz] = Relationship(back_populates="attempts")


class Assignment(SQLModel, table=True):
    """Assignment model - course requirement."""
    __tablename__ = "assignments"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    course_id: str = Field(ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    title: str = Field(max_length=255, nullable=False)
    description: str = Field(default="", nullable=False)
    xp_reward: int = Field(default=50, nullable=False)
    coin_reward: int = Field(default=100, nullable=False)

    course: Optional[Course] = Relationship(back_populates="assignments")
    submissions: List["StudentAssignmentSubmission"] = Relationship(
        back_populates="assignment",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )


class Project(SQLModel, table=True):
    """Final project model."""
    __tablename__ = "projects"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    course_id: str = Field(ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    title: str = Field(max_length=255, nullable=False)
    description: str = Field(default="", nullable=False)
    requirements_url: Optional[str] = Field(default=None, max_length=500)
    xp_reward: int = Field(default=100, nullable=False)
    coin_reward: int = Field(default=300, nullable=False)

    course: Optional[Course] = Relationship(back_populates="projects")
    submissions: List["StudentProjectSubmission"] = Relationship(
        back_populates="project",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )


class Enrollment(SQLModel, table=True):
    """Student enrollment in a course."""
    __tablename__ = "enrollments"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    student_id: str = Field(ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id: str = Field(ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    enrolled_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    completed_at: Optional[datetime] = Field(default=None)

    student: Optional["Student"] = Relationship(
        back_populates="enrollments"
    )
    course: Optional[Course] = Relationship(back_populates="enrollments")


class LessonProgress(SQLModel, table=True):
    """Tracks student lesson completion."""
    __tablename__ = "lesson_progress"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    student_id: str = Field(ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    lesson_id: str = Field(ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True)
    completed_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    student: Optional["Student"] = Relationship()
    lesson: Optional[Lesson] = Relationship(back_populates="progress_records")


class StudentAssignmentSubmission(SQLModel, table=True):
    """Student assignment submission."""
    __tablename__ = "student_assignment_submissions"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    student_id: str = Field(ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    assignment_id: str = Field(ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False, index=True)
    submission_url: str = Field(max_length=500, nullable=False)
    status: str = Field(default="submitted", nullable=False)
    score: Optional[int] = Field(default=None, ge=0, le=100)
    submitted_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    student: Optional["Student"] = Relationship()
    assignment: Optional[Assignment] = Relationship(back_populates="submissions")


class StudentProjectSubmission(SQLModel, table=True):
    """Student project submission."""
    __tablename__ = "student_project_submissions"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    student_id: str = Field(ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id: str = Field(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    submission_url: str = Field(max_length=500, nullable=False)
    status: str = Field(default="submitted", nullable=False)
    score: Optional[int] = Field(default=None, ge=0, le=100)
    feedback: Optional[str] = Field(default=None)
    submitted_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    student: Optional["Student"] = Relationship()
    project: Optional[Project] = Relationship(back_populates="submissions")
