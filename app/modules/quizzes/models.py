"""app/modules/quizzes/models.py - Quiz and quiz result models."""

from datetime import datetime
from uuid import uuid4
from sqlmodel import SQLModel, Field
from enum import Enum


class Quiz(SQLModel, table=True):
    """Quiz model - one per chapter."""
    __tablename__ = "quizzes"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    chapter_id: str = Field(foreign_key="chapters.id", nullable=False, unique=True, index=True)
    pass_score: int = Field(default=60, nullable=False, ge=0, le=100)
    xp_reward: int = Field(default=100, nullable=False)
    coin_reward: int = Field(default=25, nullable=False)


class QuizQuestion(SQLModel, table=True):
    """Quiz question with 4 options."""
    __tablename__ = "quiz_questions"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    quiz_id: str = Field(foreign_key="quizzes.id", nullable=False, index=True)
    question_text: str = Field(nullable=False)
    option_a: str = Field(max_length=500, nullable=False)
    option_b: str = Field(max_length=500, nullable=False)
    option_c: str = Field(max_length=500, nullable=False)
    option_d: str = Field(max_length=500, nullable=False)
    correct_option: str = Field(max_length=1, nullable=False)


class StudentQuizResult(SQLModel, table=True):
    """Student quiz attempt result."""
    __tablename__ = "student_quiz_results"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    student_id: str = Field(foreign_key="students.id", nullable=False, index=True)
    quiz_id: str = Field(foreign_key="quizzes.id", nullable=False, index=True)
    score: int = Field(ge=0, le=100, nullable=False)
    passed: bool = Field(nullable=False)
    attempted_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)