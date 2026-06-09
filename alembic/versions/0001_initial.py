"""alembic/versions/0001_initial.py - Initial migration for User models."""

from alembic import op
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, Enum, ForeignKey
from sqlalchemy import func
import sqlalchemy as sa
import sqlmodel.sql.sqltypes

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "students",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("country", sa.String(100), nullable=False, server_default="Bangladesh"),
        sa.Column("education_level", sa.String(100), nullable=True),
        sa.Column("experience_level", sa.String(100), nullable=True),
        sa.Column("dream_career", sa.String(255), nullable=True),
        sa.Column("xp_points", sa.Integer, nullable=False, server_default="0"),
        sa.Column("level", sa.Integer, nullable=False, server_default="1"),
        sa.Column("coins", sa.Integer, nullable=False, server_default="0"),
        sa.Column("daily_streak", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=func.now()),
    )
    op.create_index("ix_students_email", "students", ["email"])

    op.create_table(
        "admin_users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), nullable=False, server_default="content_manager"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=func.now()),
    )
    op.create_index("ix_admin_users_email", "admin_users", ["email"])


def downgrade() -> None:
    op.drop_table("admin_users")
    op.drop_table("students")
