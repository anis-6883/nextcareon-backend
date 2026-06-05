"""app/db/mixins.py - Reusable SQLModel model mixins."""

from datetime import datetime
from typing import Optional
from sqlmodel import Field


class TimestampMixin:
    """Add created_at and updated_at timestamps to models."""

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: Optional[datetime] = Field(default=None, nullable=True)


class UUIDMixin:
    """Add UUID primary key to models."""

    id: Optional[str] = Field(default=None, primary_key=True)