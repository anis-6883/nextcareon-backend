# app/models/skill.py
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

from app.models.career_path import CareerPath

class Skill(SQLModel, Table=True):
    __tablename__= "skill"

    # PK & FK
    skill_id: Optional[int] = Field(default=None, primary_key=True)
    path_id: int = Field(foreign_key="carreer_path.path_id", nullable=False,index=True)
    
    #skill info
    name: str = Field(max_length=100, nullable=False)
    category: str = Field(max_length=100, nullable=False)
    level_required: int = Field(default=1, nullable=False)

    # Progress tracking
    status: str = Field(max_length=100, default="locked", nullable=False)
    progress_pct: float = Field(default=0.0, nullable=False)

    # Timestamps
    unlock_at: Optional[datetime] = Field(default=None, nullable=True)

    # Relationships
    career_path: Optional["CareerPath"] = Relationship(back_populates="skills")
