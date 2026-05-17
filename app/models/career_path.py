# impoet file list - start
from typing import Optional, List
from datetime import datetime
from openai.resources import Skills
from sqlmodel import SQLModel, Relationship, Field

from app.models.project import Project
from app.models.resource import Resource
from app.models.user import User


class CareerPath(SQLModel, table=True):
    __tablename__= "career_path"
#Relation keys 
    path_id: Optional[int] = Field(default=None, primary_key=True) # PK
    user_id: int = Field(foreign_key="user.user_id", nullable=False, unique=True,index=True)
# Basic infos (SE/WD/CE) (CSE/CIS/SWE) 
    target_role: str = Field(max_length=100, nullable=False)
    dept: str = Field(max_length=100, nullable=False)
# AI data
    generated_by_ai: bool = Field(default=True, nullable=False)
# Stats & Progress 
    status: str = Field(max_length=100, nullable= False, default="active")
    completion_pct: int = Field(default=0.0, nullable=False)
# Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

# relationships
    user: Optional["User"] = Relationship(back_populates="career_path")
    skills: List["Skills"] = Relationship(back_populates="career_path")
    projects: list["Project"] = Relationship(back_populates="career_path")
    resources: list["Resource"] = Relationship(back_populates="career_path")