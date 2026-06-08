"""app/modules/gamification/models.py - Gamification models."""

from datetime import datetime
from typing import Optional, List
from uuid import uuid4
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON
import enum


class TransactionType(str, enum.Enum):
    """Coin transaction types."""
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"


class SourceTrigger(str, enum.Enum):
    """Source of coin transaction."""
    LESSON_COMPLETION = "LESSON_COMPLETION"
    QUIZ_PASS = "QUIZ_PASS"
    ASSIGNMENT_COMPLETION = "ASSIGNMENT_COMPLETION"
    PROJECT_COMPLETION = "PROJECT_COMPLETION"
    COURSE_COMPLETION = "COURSE_COMPLETION"
    AI_GATE_PURCHASE = "AI_GATE_PURCHASE"
    QUIZ_REATTEMPT = "QUIZ_REATTEMPT"
    ASSIGNMENT_REATTEMPT = "ASSIGNMENT_REATTEMPT"
    TEMPLATE_UNLOCK = "TEMPLATE_UNLOCK"
    PROFILE_CUSTOMIZATION = "PROFILE_CUSTOMIZATION"


class AchievementTier(str, enum.Enum):
    """Achievement badge tiers."""
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"
    PLATINUM = "PLATINUM"


class MetricType(str, enum.Enum):
    """Achievement metric types."""
    QUIZZES_PASSED = "QUIZZES_PASSED"
    PROJECTS_COMPLETED = "PROJECTS_COMPLETED"
    COINS_EARNED = "COINS_EARNED"


class ItemType(str, enum.Enum):
    """Inventory item types."""
    PORTFOLIO_TEMPLATE = "PORTFOLIO_TEMPLATE"
    RESUME_TEMPLATE = "RESUME_TEMPLATE"
    PROJECT_TEMPLATE = "PROJECT_TEMPLATE"
    DASHBOARD_THEME = "DASHBOARD_THEME"
    AVATAR = "AVATAR"


class CoinLedger(SQLModel, table=True):
    """Append-only coin transaction ledger."""
    __tablename__ = "coin_ledger"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    student_id: str = Field(foreign_key="students.id", nullable=False, index=True)
    transaction_type: TransactionType = Field(nullable=False)
    source_trigger: SourceTrigger = Field(nullable=False)
    amount: int = Field(ge=1, nullable=False)
    balance_snapshot: int = Field(nullable=False)
    description: str = Field(default="", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    student: Optional["Student"] = Relationship()


class UserBalance(SQLModel, table=True):
    """Student coin balance tracker."""
    __tablename__ = "user_balances"

    student_id: str = Field(foreign_key="students.id", primary_key=True, nullable=False)
    current_balance: int = Field(default=0, nullable=False, ge=0)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    student: Optional["Student"] = Relationship()


class Achievement(SQLModel, table=True):
    """Achievement badge definitions."""
    __tablename__ = "achievements"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    tier: AchievementTier = Field(nullable=False)
    metric_type: MetricType = Field(nullable=False)
    target_threshold: int = Field(ge=1, nullable=False)
    badge_image_url: str = Field(default="", nullable=False)

    users: List["UserAchievement"] = Relationship(
        back_populates="achievement",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class UserAchievement(SQLModel, table=True):
    """Student-achievement mapping."""
    __tablename__ = "user_achievements"

    student_id: str = Field(foreign_key="students.id", primary_key=True, nullable=False)
    achievement_id: str = Field(foreign_key="achievements.id", primary_key=True, nullable=False)
    unlocked_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    achievement: Optional[Achievement] = Relationship(back_populates="users")
    student: Optional["Student"] = Relationship()


class InventoryItem(SQLModel, table=True):
    """Store items available for purchase."""
    __tablename__ = "inventory_items"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    type: ItemType = Field(nullable=False)
    name: str = Field(max_length=255, nullable=False)
    coin_cost: int = Field(ge=1, nullable=False)
    resource_payload_json: dict = Field(default_factory=dict, sa_column=Column(JSON))

    student_inventories: List["StudentInventory"] = Relationship(
        back_populates="item",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class StudentInventory(SQLModel, table=True):
    """Student-owned inventory items."""
    __tablename__ = "student_inventory"

    student_id: str = Field(foreign_key="students.id", primary_key=True, nullable=False)
    item_id: str = Field(foreign_key="inventory_items.id", primary_key=True, nullable=False)
    purchased_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    item: Optional[InventoryItem] = Relationship(back_populates="student_inventories")
    student: Optional["Student"] = Relationship()


class AiCreditGate(SQLModel, table=True):
    """AI question credits for students."""
    __tablename__ = "ai_credit_gates"

    student_id: str = Field(foreign_key="students.id", primary_key=True, nullable=False)
    remaining_ai_questions: int = Field(default=0, nullable=False, ge=0)

    student: Optional["Student"] = Relationship()


from app.modules.users.models import Student