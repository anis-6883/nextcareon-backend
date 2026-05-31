from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class AdminAuditLog(SQLModel, table=True):
"

    __tablename__ = "admin_audit_log"

    # ── Primary Key ──────────────────────────────────────────
    log_id: Optional[int] = Field(default=None, primary_key=True)

    # ── Admin Identity ────────────────────────────────────────
    admin_id: int = Field(foreign_key="user.user_id", nullable=False, index=True)

    # ── Action Tracking ───────────────────────────────────────
    action_type: str = Field(
        max_length=100,
        nullable=False,
        index=True,
        description="e.g., 'COURSE_CREATED', 'USER_BANNED', 'RESOURCE_UPLOADED', 'USER_WARNED'"
    )

    target_id: Optional[int] = Field(
        default=None,
        nullable=True,
        index=True,
        description="Reference ID of the modified entity (course_id, user_id, resource_id, etc.)"
    )

    target_type: Optional[str] = Field(
        default=None,
        max_length=50,
        nullable=True,
        description="Type of target entity: 'COURSE', 'SKILL', 'PROJECT', 'RESOURCE', 'USER', 'WARNING'"
    )

    # ── Change Details ────────────────────────────────────────
    details: Optional[str] = Field(
        default=None,
        max_length=1000,
        nullable=True,
        description="JSON string with detailed change data (old/new values, reason, etc.)"
    )

    # ── Status ────────────────────────────────────────────────
    status: str = Field(
        default="success",
        max_length=20,
        description="'success' or 'failed'"
    )

    error_message: Optional[str] = Field(
        default=None,
        max_length=500,
        nullable=True,
        description="Error message if status is 'failed'"
    )

    # ── Timestamps ────────────────────────────────────────────
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,
        description="Auto-generated on creation (append-only)"
    )

    ip_address: Optional[str] = Field(
        default=None,
        max_length=45,
        nullable=True,
        description="IP address of the requesting admin (IPv4 or IPv6)"
    )

    user_agent: Optional[str] = Field(
        default=None,
        max_length=500,
        nullable=True,
        description="User-Agent header from the request"
    )
