from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.career_path import CareerPath


class Skill(SQLModel, table=True):

    __tablename__ = "skill"
    skill_id: Optional[int] = Field(default=None, primary_key=True)
    path_id: int = Field(foreign_key="career_path.path_id", nullable=False, index=True)
    name: str = Field(max_length=100, nullable=False)
    category: str = Field(max_length=50, nullable=False)
    level_required: int = Field(default=1, nullable=False)
    status: str = Field(default="locked", max_length=20, nullable=False)
    progress_pct: float = Field(default=0.0, nullable=False)   
    unlock_at: Optional[datetime] = Field(default=None, nullable=True)



    career_path: Optional["CareerPath"] = Relationship(back_populates="skills")