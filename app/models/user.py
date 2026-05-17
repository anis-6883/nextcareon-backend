# impoet file list - start
from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

from app.models.career_path import CareerPath
# impoet file list - end

class User(SQLModel, table=True): #As we can see in the ERD diagram 1:1 / 1:M relation 
    __tablename__ = "user"

    user_id: Optional[int] = Field(default=None, primary_key=True) # PK
 
# Others Identifying Information
    name: str = Field(max_length=100, nullable= False)
    email: str = Field(max_length=100, nullable=False, unique=True, index=True)
    password: str = Field(max_length=100, nullable=False)
    dept: str = Field(max_length=100, nullable=False)

# Game related information
    level: int = Field(default=1, nullable=False)
    xp_point: int = Field(default=0, nullable=False)
    dailystreak: int = Field(default=0, nullable=False)

# Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

# relationships
    career_path: Optional["CareerPath"] = Relationship(back_populates="user")
    milestones: list["Milestone"] = Relationship(back_populates="user")

    