"""alembic/versions/0002_career_score_models.py - Career score and audit models."""

from alembic import op
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, Enum, ForeignKey, Float
from sqlalchemy import func
import sqlalchemy as sa


revision = "0002_career_score_models"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "career_scores",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("student_id", sa.String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("course_completion_score", sa.Float, nullable=False, server_default="0"),
        sa.Column("quiz_performance_score", sa.Float, nullable=False, server_default="0"),
        sa.Column("project_quality_score", sa.Float, nullable=False, server_default="0"),
        sa.Column("portfolio_strength_score", sa.Float, nullable=False, server_default="0"),
        sa.Column("mock_interview_score", sa.Float, nullable=False, server_default="0"),
        sa.Column("total_career_score", sa.Float, nullable=False, server_default="0"),
        sa.Column("last_calculated_at", sa.DateTime, nullable=True),
    )
    op.create_index("ix_career_scores_student_id", "career_scores", ["student_id"])
    op.create_index("ix_career_scores_total", "career_scores", ["total_career_score"])

    op.create_table(
        "career_score_history",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("student_id", sa.String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False),
        sa.Column("total_career_score", sa.Float, nullable=False),
        sa.Column("recorded_at", sa.DateTime, nullable=False, server_default=func.now()),
    )
    op.create_index("ix_career_score_history_student_id", "career_score_history", ["student_id"])

    op.create_table(
        "admin_score_override_audit_log",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("student_id", sa.String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False),
        sa.Column("admin_id", sa.String(36), ForeignKey("admin_users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("metric_changed", sa.String(50), nullable=False),
        sa.Column("old_value", sa.Float, nullable=False),
        sa.Column("new_value", sa.Float, nullable=False),
        sa.Column("reason_for_override", sa.Text, nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=func.now()),
    )
    op.create_index("ix_admin_override_student_id", "admin_score_override_audit_log", ["student_id"])
    op.create_index("ix_admin_override_admin_id", "admin_score_override_audit_log", ["admin_id"])

    op.create_table(
        "mock_interview_credits",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("student_id", sa.String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("available_credits", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_purchased_or_earned", sa.Integer, nullable=False, server_default="0"),
    )
    op.create_index("ix_mock_interview_credits_student_id", "mock_interview_credits", ["student_id"])

    op.create_table(
        "portfolio_projects",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("student_id", sa.String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.String, nullable=False, server_default=""),
        sa.Column("repository_url", sa.String(500), nullable=False, server_default=""),
        sa.Column("live_url", sa.String(500), nullable=False, server_default=""),
        sa.Column("admin_quality_rating", sa.Float, nullable=True),
        sa.Column("reviewed_at", sa.DateTime, nullable=True),
        sa.Column("reviewed_by", sa.String(36), ForeignKey("admin_users.id", ondelete="SET NULL"), nullable=True),
    )
    op.create_index("ix_portfolio_projects_student_id", "portfolio_projects", ["student_id"])


def downgrade() -> None:
    op.drop_table("portfolio_projects")
    op.drop_table("mock_interview_credits")
    op.drop_table("admin_score_override_audit_log")
    op.drop_table("career_score_history")
    op.drop_table("career_scores")