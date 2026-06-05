"""app/modules/career_score/calculator.py - Career readiness score computation."""

from typing import Optional
from app.core.config import settings


def calculate_career_readiness_score(
    course_completion_pct: float,
    quiz_avg_score: float,
    project_quality_avg: float,
    portfolio_strength: float,
    mock_interview_score: Optional[float],
) -> int:
    """
    Calculate weighted career readiness score.
    
    Weights (from config):
    - Course Completion: 15%
    - Quiz Performance: 15%
    - Project Quality: 30%
    - Portfolio Strength: 20%
    - Mock Interview: 20%
    """
    weights = settings.score_weights
    
    score = (
        course_completion_pct * weights["course_completion"] / 100 +
        quiz_avg_score * weights["quiz_performance"] / 100 +
        project_quality_avg * weights["project_quality"] / 100 +
        portfolio_strength * weights["portfolio_strength"] / 100 +
        (mock_interview_score or 0) * weights["mock_interview"] / 100
    )
    
    return int(score)


def calculate_portfolio_strength(portfolio_count: int) -> float:
    """
    Calculate portfolio strength based on project count.
    Target: 5 projects for full strength.
    """
    return min(portfolio_count / 5 * 100, 100)