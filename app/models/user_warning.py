from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class UserWarning(SQLModel, table=True):
    """
    Formal warning record for users issued by administrators.
    Used to track violations and progressive discipline.
    """

    __tablename__ = "user_warning"

    # ── Primary Key ──────────────────────────────────────────
    warning_id: Optional[int] = Field(default=None, primary_key=True)

    # ── User & Admin Identity ─────────────────────────────────
    user_id: int = Field(foreign_key="user.user_id", nullable=False, index=True)
    admin_id: int = Field(foreign_key="user.user_id", nullable=False, index=True)

    # ── Warning Details ───────────────────────────────────────
    severity: str = Field(
        max_length=20,
        nullable=False,
        description="'low', 'medium', 'high', 'critical'"
    )
    reason: str = Field(
        max_length=500,
        nullable=False,
        description="Reason for the warning (e.g., 'Plagiarism detected', 'Violating community guidelines')"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        nullable=True,
        description="Detailed description of the violation"
    )

    # ── Status ─────────────────────────────────────────────────
    status: str = Field(
        default="active",
        max_length=20,
        description="'active', 'acknowledged', 'dismissed', 'escalated'"
    )
    is_active: bool = Field(default=True, nullable=False, description="Whether warning is currently active")

    # ── Response Tracking ─────────────────────────────────────
    user_acknowledgement: bool = Field(default=False, nullable=False, description="User has acknowledged warning")
    acknowledged_at: Optional[datetime] = Field(default=None, nullable=True)
    user_response: Optional[str] = Field(
        default=None,
        max_length=1000,
        nullable=True,
        description="User's response or appeal to the warning"
    )

    # ── Timeline ───────────────────────────────────────────────
    issued_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)
    expires_at: Optional[datetime] = Field(
        default=None,
        nullable=True,
        description="Date when warning expires (warnings may auto-clear after duration)"
    )

    # ── Escalation ─────────────────────────────────────────────
    escalation_count: int = Field(default=0, nullable=False, description="Number of times escalated")
    last_escalated_at: Optional[datetime] = Field(default=None, nullable=True)
    escalation_reason: Optional[str] = Field(
        default=None,
        max_length=500,
        nullable=True,
        description="Reason for most recent escalation"
    )

    # ── Resolution ─────────────────────────────────────────────
    resolved_at: Optional[datetime] = Field(default=None, nullable=True)
    resolution_notes: Optional[str] = Field(
        default=None,
        max_length=1000,
        nullable=True,
        description="Notes on how the warning was resolved"
    )

    # ── Metadata ───────────────────────────────────────────────
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
