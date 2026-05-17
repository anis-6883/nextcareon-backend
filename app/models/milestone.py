from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

from app.models.user import User


class Milestone(SQLModel, table=True):
    __tablename__ = "milestone"


    milestone_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.user_id", nullable=False, index=True)
    title: str = Field(max_length=150, nullable=False)
    # e.g. "Cloud Native Guru", "Clean Coder"

    xp_reward: int = Field(default=0, nullable=False)
    # bonus XP granted when this milestone is earned

    badge_icon: Optional[str] = Field(default=None, max_length=100, nullable=True)
    # icon identifier string e.g. "cloud-guru" mapped to a frontend asset

    achieve_date: Optional[datetime] = Field(default=None, nullable=True)
    # set to datetime.utcnow() by xp_service when milestone is triggered

    level_threshold: int = Field(nullable=False)
    # the user.level value that triggers this milestone
    # e.g. level_threshold=10 → awarded when user hits level 10

    # ── Relationships ─────────────────────────────────────────
    user: Optional["User"] = Relationship(back_populates="milestones")
    