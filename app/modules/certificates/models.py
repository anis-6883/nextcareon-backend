"""app/modules/certificates/models.py - Certificate model."""

from datetime import datetime
from uuid import uuid4
from sqlmodel import SQLModel, Field


class Certificate(SQLModel, table=True):
    """Certificate awarded for course completion."""
    __tablename__ = "certificates"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    student_id: str = Field(foreign_key="students.id", nullable=False, index=True)
    course_id: str = Field(foreign_key="courses.id", nullable=False, index=True)
    certificate_url: str = Field(max_length=500, nullable=False)
    issued_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
