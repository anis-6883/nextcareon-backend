from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.career_path import CareerPath


class Project(SQLModel, table=True):


    __tablename__ = "project"


    project_id: Optional[int] = Field(default=None, primary_key=True)


    path_id: int = Field(foreign_key="career_path.path_id", nullable=False, index=True)


    title: str = Field(max_length=150, nullable=False)
    description: str = Field(max_length=1000, nullable=False)


    level_required: int = Field(default=1, nullable=False)
    # project is locked until user.level >= level_required


    skills_needed: str = Field(max_length=500, nullable=False)
    # comma-separated skill names e.g. "Python, Docker, REST APIs"
    # kept as a string to match ER diagram; can be normalised later

    status: str = Field(default="locked", max_length=20, nullable=False)
    # status options: "locked" | "unlocked" | "in_progress" | "completed"
    xp_reward: int = Field(default=0, nullable=False)
    # XP awarded to the user on project completion


    career_path: Optional["CareerPath"] = Relationship(back_populates="projects")