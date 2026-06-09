"""app/modules/auth/models.py - Auth-related models (if any)."""

from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class RefreshToken(SQLModel, table=True):
    """Refresh token storage for revocation support."""
    __tablename__ = "refresh_tokens"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    token_hash: str = Field(max_length=255)
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
