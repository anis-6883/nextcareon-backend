"""app/modules/gamification/models.py - Coins, achievements, templates, customizations."""

from datetime import datetime
from typing import Optional
from uuid import uuid4
from sqlmodel import SQLModel, Field
from enum import Enum


class ActionType(str, Enum):
    """Coin rule action types."""
    WATCH_LESSON = "watch_lesson"
    PASS_QUIZ = "pass_quiz"
    COMPLETE_ASSIGNMENT = "complete_assignment"
    COMPLETE_PROJECT = "complete_project"
    COMPLETE_COURSE = "complete_course"


class TransactionType(str, Enum):
    """Coin transaction type."""
    EARN = "earn"
    SPEND = "spend"


class Tier(str, Enum):
    """Achievement tier."""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


class Category(str, Enum):
    """Customization item category."""
    BADGE = "badge"
    THEME = "theme"
    AVATAR = "avatar"


class CoinRule(SQLModel, table=True):
    """Defines coin reward amounts for actions."""
    __tablename__ = "coin_rules"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    action_type: ActionType = Field(nullable=False)
    coin_reward: int = Field(nullable=False, gt=0)


class CoinTransaction(SQLModel, table=True):
    """Record of coin earnings/spending."""
    __tablename__ = "coin_transactions"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    student_id: str = Field(foreign_key="students.id", nullable=False, index=True)
    coin_rule_id: Optional[str] = Field(default=None, foreign_key="coin_rules.id", nullable=True)
    transaction_type: TransactionType = Field(nullable=False)
    amount: int = Field(nullable=False)
    description: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class Achievement(SQLModel, table=True):
    """Achievement definition (badge)."""
    __tablename__ = "achievements"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    name: str = Field(max_length=255, nullable=False)
    badge_icon_url: str = Field(max_length=500, nullable=False)
    tier: Tier = Field(default=Tier.BRONZE, nullable=False)
    required_value: int = Field(nullable=False)


class StudentAchievement(SQLModel, table=True):
    """Student earned achievement."""
    __tablename__ = "student_achievements"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    student_id: str = Field(foreign_key="students.id", nullable=False, index=True)
    achievement_id: str = Field(foreign_key="achievements.id", nullable=False, index=True)
    earned_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class Template(SQLModel, table=True):
    """Premium template for purchase."""
    __tablename__ = "templates"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    type: str = Field(max_length=50, nullable=False)
    name: str = Field(max_length=255, nullable=False)
    preview_url: str = Field(max_length=500, nullable=False)
    download_url: str = Field(max_length=500, nullable=False)
    coin_cost: int = Field(nullable=False, gt=0)


class StudentTemplatePurchase(SQLModel, table=True):
    """Student purchased template."""
    __tablename__ = "student_template_purchases"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    student_id: str = Field(foreign_key="students.id", nullable=False, index=True)
    template_id: str = Field(foreign_key="templates.id", nullable=False, index=True)
    purchased_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class CustomizationItem(SQLModel, table=True):
    """Profile customization item."""
    __tablename__ = "customization_items"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    category: Category = Field(nullable=False)
    name: str = Field(max_length=255, nullable=False)
    asset_url: str = Field(max_length=500, nullable=False)
    coin_cost: int = Field(nullable=False, gt=0)


class StudentCustomization(SQLModel, table=True):
    """Student equipped customization item."""
    __tablename__ = "student_customizations"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    student_id: str = Field(foreign_key="students.id", nullable=False, index=True)
    customization_item_id: str = Field(foreign_key="customization_items.id", nullable=False, index=True)
    equipped_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)