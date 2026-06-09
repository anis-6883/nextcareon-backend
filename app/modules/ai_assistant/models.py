"""app/modules/ai_assistant/models.py - AI assistant models."""

from datetime import datetime
from typing import Optional, List
from uuid import uuid4
from sqlmodel import SQLModel, Field, Relationship
import enum


class AiConversation(SQLModel, table=True):
    """AI conversation history."""
    __tablename__ = "ai_conversations"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    student_id: str = Field(foreign_key="students.id", nullable=False, index=True)
    course_id: Optional[str] = Field(default=None, foreign_key="courses.id", nullable=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    student: Optional["Student"] = Relationship()
    messages: List["AiMessage"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class AiMessage(SQLModel, table=True):
    """AI message within a conversation."""
    __tablename__ = "ai_messages"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    conversation_id: str = Field(foreign_key="ai_conversations.id", nullable=False)
    role: str = Field(nullable=False)
    content: str = Field(nullable=False)
    tokens_used: int = Field(default=0, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    conversation: Optional[AiConversation] = Relationship(back_populates="messages")


class AiUsageLog(SQLModel, table=True):
    """Log of student AI assistant usage."""
    __tablename__ = "ai_usage_logs"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    student_id: str = Field(foreign_key="students.id", nullable=False, index=True)
    endpoint_accessed: str = Field(default="", nullable=False)
    total_tokens: int = Field(default=0, nullable=False)
    response_time_ms: int = Field(default=0, nullable=False)
    timestamp: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    student: Optional["Student"] = Relationship()


class LessonChunks(SQLModel, table=True):
    """Vector embeddings for lesson content chunks."""
    __tablename__ = "lesson_chunks"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    lesson_id: str = Field(foreign_key="lessons.id", nullable=False, index=True)
    chunk_index: int = Field(nullable=False)
    content_text: str = Field(nullable=False)
    embedding: Optional[str] = Field(default=None, nullable=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    lesson: Optional["Lesson"] = Relationship()


from app.modules.users.models import Student
from app.modules.courses.models import Lesson
