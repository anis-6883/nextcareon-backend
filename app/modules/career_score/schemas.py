"""app/modules/career_score/schemas.py - Pydantic schemas for career score API."""

from typing import Optional
from pydantic import BaseModel
from app.modules.career_score.models import MetricType


class CareerScoreResponse(BaseModel):
    """Response schema for career score."""
    id: str
    student_id: str
    course_completion_score: float
    quiz_performance_score: float
    project_quality_score: float
    portfolio_strength_score: float
    mock_interview_score: float
    total_career_score: float
    last_calculated_at: Optional[str] = None


class ScoreTimelineEntry(BaseModel):
    """Single entry in score timeline."""
    score: float
    recorded_at: str


class ScoreTimelineResponse(BaseModel):
    """Response schema for score timeline."""
    student_id: str
    timeline: list[ScoreTimelineEntry]


class StudentRankingResponse(BaseModel):
    """Response schema for student ranking."""
    student_id: str
    rank: int
    percentile: float
    total_students: int


class StudentPublicProfileResponse(BaseModel):
    """Response schema for public student profile."""
    student_id: str
    full_name: str
    dream_career: Optional[str] = None
    education_level: Optional[str] = None
    experience_level: Optional[str] = None
    career_score: dict
    portfolio_projects: list


class ScoreOverrideRequest(BaseModel):
    """Request schema for admin score override."""
    student_id: str
    metric: MetricType
    new_value: float
    reason: str