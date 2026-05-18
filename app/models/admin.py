from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class Admin(SQLModel, table=True):

    __tablename__ = "admin"

    # ── Primary Key ──────────────────────────────────────────
    admin_id: Optional[int] = Field(default=None, primary_key=True)

    # ── Identity fields ───────────────────────────────────────
    username: str = Field(max_length=100, nullable=False, unique=True, index=True)
    password: str = Field(max_length=255, nullable=False)   # bcrypt hash

    # ── Admin Status ───────────────────────────────────────────
    is_active: bool = Field(default=True, nullable=False)
    permissions: str = Field(default="all", max_length=255, nullable=False)  # CSV of permissions
    last_login: Optional[datetime] = Field(default=None)

    # ── Timestamps ────────────────────────────────────────────
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
