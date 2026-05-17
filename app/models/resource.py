from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

from app.models.career_path import CareerPath


class Resource(SQLModel, table=True):
    __tablename__ = "resource"

    # ── Primary Key 
    resource_id: Optional[int] = Field(default=None, primary_key=True)
    # ── Foreign Key 
    path_id: int = Field(foreign_key="career_path.path_id", nullable=False, index=True)
    title: str = Field(max_length=200, nullable=False)
    type: str = Field(max_length=50, nullable=False)
    # type options: "video" | "documentation" | "article" | "cheat_sheet" | "whitepaper"

    url: str = Field(max_length=500, nullable=False)

    # ── Level gate 
    level_range: str = Field(max_length=20, nullable=False)
    # stored as "1-10", "11-20", "31-42" etc. to match ER diagram
    # format: "{min_level}-{max_level}" — parsed in the service layer

    is_locked: bool = Field(default=True, nullable=False)
    # flipped to False by resource_service when user meets level_range

    # ── Relationships 
    career_path: Optional["CareerPath"] = Relationship(back_populates="resources")