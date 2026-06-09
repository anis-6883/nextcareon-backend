"""alembic/versions/0004_ai_assistant_models.py - AI assistant models with pgvector."""

from alembic import op
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy import func
import sqlalchemy as sa


revision = "0004_ai_assistant_models"
down_revision = "0003_gamification_models"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    
    op.create_table(
        "ai_conversations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("student_id", sa.String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False),
        sa.Column("course_id", sa.String(36), ForeignKey("courses.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=func.now()),
    )
    op.create_index("ix_ai_conversations_student_id", "ai_conversations", ["student_id"])

    op.create_table(
        "ai_messages",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("conversation_id", sa.String(36), ForeignKey("ai_conversations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("tokens_used", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=func.now()),
    )

    op.create_table(
        "ai_usage_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("student_id", sa.String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False),
        sa.Column("endpoint_accessed", sa.String(100), nullable=False, server_default=""),
        sa.Column("total_tokens", sa.Integer, nullable=False, server_default="0"),
        sa.Column("response_time_ms", sa.Integer, nullable=False, server_default="0"),
        sa.Column("timestamp", sa.DateTime, nullable=False, server_default=func.now()),
    )
    op.create_index("ix_ai_usage_logs_student_id", "ai_usage_logs", ["student_id"])

    op.create_table(
        "lesson_chunks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("lesson_id", sa.String(36), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False),
        sa.Column("chunk_index", sa.Integer, nullable=False),
        sa.Column("content_text", sa.Text, nullable=False),
        sa.Column("embedding", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=func.now()),
    )
    op.create_index("ix_lesson_chunks_lesson_id", "lesson_chunks", ["lesson_id"])


def downgrade() -> None:
    op.drop_table("lesson_chunks")
    op.drop_table("ai_usage_logs")
    op.drop_table("ai_messages")
    op.drop_table("ai_conversations")
