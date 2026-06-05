"""app/modules/ai_assistant/models.py - AI models."""

from datetime import datetime
from typing import Optional
from uuid import uuid4
from sqlmodel import SQLModel, Field

class AIUsageLog(SQLModel, table=True):
    """Log of student AI assistant usage."""
    __tablename__ = "ai_usage_logs"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    student_id: str = Field(foreign_key="students.id", nullable=False, index=True)
    question: str = Field(nullable=False)
    answer: str = Field(nullable=False)
    coin_cost: int = Field(default=0, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)