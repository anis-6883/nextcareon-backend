"""app/modules/gamification/schemas.py - Pydantic schemas for gamification API."""

from typing import Optional
from pydantic import BaseModel
from app.modules.gamification.models import AchievementTier, MetricType, ItemType


class BalanceResponse(BaseModel):
    """Response schema for coin balance."""
    student_id: str
    balance: int


class LeaderboardEntry(BaseModel):
    """Single leaderboard entry."""
    student_id: str
    coins: int


class LeaderboardResponse(BaseModel):
    """Response schema for leaderboard."""
    entries: list[LeaderboardEntry]


class PurchaseRequest(BaseModel):
    """Request schema for item purchase."""
    item_id: str


class PurchaseResponse(BaseModel):
    """Response schema for item purchase."""
    success: bool
    message: str


class AiExchangeResponse(BaseModel):
    """Response schema for AI credit exchange."""
    success: bool
    message: str
    remaining_ai_questions: int


class AchievementResponse(BaseModel):
    """Response schema for achievement."""
    id: str
    tier: AchievementTier
    metric_type: MetricType
    target_threshold: int
    badge_image_url: str
    unlocked_at: str


class StoreItemResponse(BaseModel):
    """Response schema for store item."""
    id: str
    type: ItemType
    name: str
    coin_cost: int
    resource_payload: dict
