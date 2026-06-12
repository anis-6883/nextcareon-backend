"""app/modules/admin/audit_models.py - Audit logging models for admin operations."""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import uuid4
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON
import enum


class AuditActionType(str, enum.Enum):
    """Types of audit actions."""
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    OVERRIDE = "OVERRIDE"


class AdminAuditLog(SQLModel, table=True):
    """Immutable audit log for all admin operations."""
    __tablename__ = "admin_audit_logs"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    admin_id: str = Field(foreign_key="admin_users.id", nullable=False, index=True)
    entity_type: str = Field(
        max_length=100,
        nullable=False,
        index=True,
        description="Entity type being modified (e.g., 'Course', 'User', 'Quiz')"
    )
    entity_id: str = Field(
        max_length=255,
        nullable=False,
        index=True,
        description="ID of the entity being modified"
    )
    action_executed: AuditActionType = Field(nullable=False, index=True)
    
    # Delta payload: captures previous vs new state
    delta_payload_json: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Previous and current state: {'before': {...}, 'after': {...}}"
    )
    
    reason_text: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Optional reason for the operation"
    )
    
    # Metadata
    ip_address: Optional[str] = Field(default=None, max_length=50)
    user_agent: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)

    admin: Optional["AdminUser"] = Relationship()


class AdminScopeOverrideLog(SQLModel, table=True):
    """Specialized audit log for sensitive score overrides."""
    __tablename__ = "admin_scope_override_logs"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    admin_id: str = Field(foreign_key="admin_users.id", nullable=False, index=True)
    student_id: str = Field(foreign_key="students.id", nullable=False, index=True)
    
    metric_type: str = Field(
        max_length=100,
        nullable=False,
        description="Metric type being overridden"
    )
    previous_value: float = Field(nullable=False)
    new_value: float = Field(nullable=False)
    override_reason: str = Field(max_length=1000, nullable=False)
    
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)

    admin: Optional["AdminUser"] = Relationship()
    student: Optional["Student"] = Relationship()


from app.modules.users.models import AdminUser, Student
