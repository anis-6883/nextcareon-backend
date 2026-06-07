"""app/modules/assignments/schemas.py - Assignment schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AssignmentCreate(BaseModel):
    title: str
    description: str = ""
    xp_reward: int = 50
    coin_reward: int = 100


class AssignmentRead(BaseModel):
    id: str
    course_id: str
    title: str
    description: str
    xp_reward: int
    coin_reward: int

    class Config:
        from_attributes = True


class ProjectCreate(BaseModel):
    title: str
    description: str = ""
    requirements_url: Optional[str] = None
    xp_reward: int = 100
    coin_reward: int = 300


class ProjectRead(BaseModel):
    id: str
    course_id: str
    title: str
    description: str
    requirements_url: Optional[str]
    xp_reward: int
    coin_reward: int

    class Config:
        from_attributes = True


class AssignmentSubmit(BaseModel):
    assignment_id: str
    submission_url: str


class ProjectSubmit(BaseModel):
    project_id: str
    submission_url: str


class SubmissionRead(BaseModel):
    id: str
    assignment_id: Optional[str] = None
    project_id: Optional[str] = None
    submission_url: str
    status: str
    score: Optional[int]
    submitted_at: datetime

    class Config:
        from_attributes = True