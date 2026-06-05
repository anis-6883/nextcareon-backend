"""app/modules/assignments/schemas.py - Assignment schemas."""

from datetime import datetime
from pydantic import BaseModel


class AssignmentRead(BaseModel):
    id: str
    title: str
    description: str


class ProjectRead(BaseModel):
    id: str
    title: str
    description: str


class ProjectSubmit(BaseModel):
    submission_url: str