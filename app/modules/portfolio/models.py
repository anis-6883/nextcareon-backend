"""app/modules/portfolio/models.py - Portfolio project models."""

from datetime import datetime
from uuid import uuid4
from sqlmodel import SQLModel, Field


class PortfolioProject(SQLModel, table=True):
    """Student portfolio project."""
    __tablename__ = "portfolio_projects"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    student_id: str = Field(foreign_key="students.id", nullable=False, index=True)
    title: str = Field(max_length=255, nullable=False)
    description: str = Field(default="", nullable=False)
    project_url: str = Field(default="", max_length=500, nullable=False)
    github_url: str = Field(default="", max_length=500, nullable=False)
    quality_rating: int = Field(default=1, nullable=False, ge=1, le=5)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)