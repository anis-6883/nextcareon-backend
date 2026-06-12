"""alembic/versions/0005_admin_audit_logs.py - Add admin audit logging tables."""

from alembic import op
from sqlalchemy import Column, String, Integer, DateTime, Text, Enum, ForeignKey, JSON
from sqlalchemy import func
import sqlalchemy as sa


revision = "0005_admin_audit_logs"
down_revision = "0004_ai_assistant_models"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create audit log tables."""
    
    # Create admin_audit_logs table
    op.create_table(
        "admin_audit_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("admin_id", sa.String(36), nullable=False, index=True),
        sa.Column("entity_type", sa.String(100), nullable=False, index=True),
        sa.Column("entity_id", sa.String(255), nullable=False, index=True),
        sa.Column("action_executed", sa.String(50), nullable=False, index=True),
        sa.Column("delta_payload_json", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("reason_text", sa.String(1000), nullable=True),
        sa.Column("ip_address", sa.String(50), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=func.now(), index=True),
        sa.ForeignKeyConstraint(["admin_id"], ["admin_users.id"], ondelete="CASCADE"),
    )

    # Create admin_scope_override_logs table (specialized log for score overrides)
    op.create_table(
        "admin_scope_override_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("admin_id", sa.String(36), nullable=False, index=True),
        sa.Column("student_id", sa.String(36), nullable=False, index=True),
        sa.Column("metric_type", sa.String(100), nullable=False),
        sa.Column("previous_value", sa.Float, nullable=False),
        sa.Column("new_value", sa.Float, nullable=False),
        sa.Column("override_reason", sa.String(1000), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=func.now(), index=True),
        sa.ForeignKeyConstraint(["admin_id"], ["admin_users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
    )

    # Create indexes for common queries
    op.create_index("ix_admin_audit_logs_entity_type", "admin_audit_logs", ["entity_type", "entity_id"])
    op.create_index("ix_admin_audit_logs_admin_id", "admin_audit_logs", ["admin_id", "created_at"])
    op.create_index("ix_admin_scope_override_logs_student", "admin_scope_override_logs", ["student_id", "created_at"])


def downgrade() -> None:
    """Drop audit log tables."""
    op.drop_table("admin_scope_override_logs")
    op.drop_table("admin_audit_logs")
