"""alembic/versions/0003_gamification_models.py - Gamification tables."""

from alembic import op
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, Enum, ForeignKey, Float
from sqlalchemy import func
import sqlalchemy as sa


revision = "0003_gamification_models"
down_revision = "0002_career_score_models"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "coin_ledger",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("student_id", sa.String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False),
        sa.Column("transaction_type", sa.String(20), nullable=False),
        sa.Column("source_trigger", sa.String(50), nullable=False),
        sa.Column("amount", sa.Integer, nullable=False),
        sa.Column("balance_snapshot", sa.Integer, nullable=False),
        sa.Column("description", sa.Text, nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=func.now()),
    )
    op.create_index("ix_coin_ledger_student_id", "coin_ledger", ["student_id"])
    op.create_index("ix_coin_ledger_created_at", "coin_ledger", ["created_at"])

    op.create_table(
        "user_balances",
        sa.Column("student_id", sa.String(36), ForeignKey("students.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("current_balance", sa.Integer, nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=func.now()),
    )

    op.create_table(
        "achievements",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tier", sa.String(20), nullable=False),
        sa.Column("metric_type", sa.String(30), nullable=False),
        sa.Column("target_threshold", sa.Integer, nullable=False),
        sa.Column("badge_image_url", sa.String(500), nullable=False, server_default=""),
    )

    op.create_table(
        "user_achievements",
        sa.Column("student_id", sa.String(36), ForeignKey("students.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("achievement_id", sa.String(36), ForeignKey("achievements.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("unlocked_at", sa.DateTime, nullable=False, server_default=func.now()),
    )
    op.create_index("ix_user_achievements_student_id", "user_achievements", ["student_id"])

    op.create_table(
        "inventory_items",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("type", sa.String(30), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("coin_cost", sa.Integer, nullable=False),
        sa.Column("resource_payload_json", sa.Text, nullable=False, server_default="{}"),
    )

    op.create_table(
        "student_inventory",
        sa.Column("student_id", sa.String(36), ForeignKey("students.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("item_id", sa.String(36), ForeignKey("inventory_items.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("purchased_at", sa.DateTime, nullable=False, server_default=func.now()),
    )

    op.create_table(
        "ai_credit_gates",
        sa.Column("student_id", sa.String(36), ForeignKey("students.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("remaining_ai_questions", sa.Integer, nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_table("ai_credit_gates")
    op.drop_table("student_inventory")
    op.drop_table("inventory_items")
    op.drop_table("user_achievements")
    op.drop_table("achievements")
    op.drop_table("user_balances")
    op.drop_table("coin_ledger")
