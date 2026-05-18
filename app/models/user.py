from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.career_path import CareerPath
    from app.models.milestone import Milestone


class User(SQLModel, table=True):

    __tablename__ = "user"

    user_id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, nullable=False)
    email: str = Field(max_length=255, nullable=False, unique=True, index=True)
    password: str = Field(max_length=255, nullable=False)   # bcrypt hash stored here
    level: int = Field(default=1, nullable=False)
    xp_point: int = Field(default=0, nullable=False)
    dept: str = Field(max_length=50, nullable=False)        # e.g. "CSE", "CIS", "SWE"
    dailystreak: int = Field(default=0, nullable=False)
    is_active: bool = Field(default=True, nullable=False)
    role: str = Field(default="user", max_length=20, nullable=False)  # "user" or "admin"
    last_login: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    career_path: Optional["CareerPath"] = Relationship(back_populates="user")
    milestones: List["Milestone"] = Relationship(back_populates="user")