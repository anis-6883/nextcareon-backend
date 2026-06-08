"""app/modules/portfolio/models.py - Portfolio project models."""

from datetime import datetime
from typing import Optional
from uuid import uuid4
from sqlmodel import SQLModel, Field, Relationship


class PortfolioProject(SQLModel, table=True):
    """Student portfolio project."""
    __tablename__ = "portfolio_projects"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    student_id: str = Field(foreign_key="students.id", nullable=False, index=True)
    title: str = Field(max_length=255, nullable=False)
    description: str = Field(default="", nullable=False)
    repository_url: str = Field(default="", max_length=500, nullable=False)
    live_url: str = Field(default="", max_length=500, nullable=False)
    admin_quality_rating: Optional[float] = Field(default=None, nullable=True, ge=0, le=100)
    reviewed_at: Optional[datetime] = Field(default=None, nullable=True)
    reviewed_by: Optional[str] = Field(default=None, foreign_key="admin_users.id", nullable=True)

    student: Optional["Student"] = Relationship()
    reviewer: Optional["AdminUser"] = Relationship()


from app.modules.users.models import Student, AdminUser