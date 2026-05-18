from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

# Guard imports inside TYPE_CHECKING so they run ONLY during type analysis,
# completely preventing the runtime circular import error.
if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.resource import Resource
    from app.models.skill import Skill
    from app.models.user import User


class CareerPath(SQLModel, table=True):

    __tablename__ = "career_path"

   
    path_id: Optional[int] = Field(default=None, primary_key=True)


    user_id: int = Field(foreign_key="user.user_id", nullable=False, unique=True, index=True)


    target_role: str = Field(max_length=100, nullable=False)    # e.g. "Software Engineer"
    dept: str = Field(max_length=50, nullable=False)            # mirrors user.dept at time of generation


    generated_by_ai: bool = Field(default=True, nullable=False) # always True for AI-generated paths


    status: str = Field(default="active", max_length=20, nullable=False)
    # status options: "active" | "completed" | "paused"
    completion_pct: float = Field(default=0.0, nullable=False)  # 0.0 → 100.0

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


    # Keeping the string-forward references ensures SQLModel can link them later
    user: Optional["User"] = Relationship(back_populates="career_path")
    skills: List["Skill"] = Relationship(back_populates="career_path")
    projects: List["Project"] = Relationship(back_populates="career_path")
    resources: List["Resource"] = Relationship(back_populates="career_path")