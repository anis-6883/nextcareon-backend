"""app/modules/career_score/calculator.py - Career readiness score computation."""

from typing import Optional
from app.core.config import settings


SCORE_WEIGHTS = {
    "course_completion": 15,
    "quiz_performance": 15,
    "project_quality": 30,
    "portfolio_strength": 20,
    "mock_interview": 20,
}


def calculate_career_readiness_score(
    course_completion_score: float,
    quiz_performance_score: float,
    project_quality_score: float,
    portfolio_strength_score: float,
    mock_interview_score: Optional[float],
) -> float:
    """
    Calculate weighted career readiness score.
    
    Weights:
    - Course Completion: 15%
    - Quiz Performance: 15%
    - Project Quality: 30%
    - Portfolio Strength: 20%
    - Mock Interview: 20%
    
    Returns total score as float (0.0 to 100.0).
    """
    weights = settings.score_weights if hasattr(settings, 'score_weights') else SCORE_WEIGHTS
    
    course_weight = weights.get("course_completion", 15) / 100
    quiz_weight = weights.get("quiz_performance", 15) / 100
    project_weight = weights.get("project_quality", 30) / 100
    portfolio_weight = weights.get("portfolio_strength", 20) / 100
    interview_weight = weights.get("mock_interview", 20) / 100
    
    score = (
        (course_completion_score or 0) * course_weight +
        (quiz_performance_score or 0) * quiz_weight +
        (project_quality_score or 0) * project_weight +
        (portfolio_strength_score or 0) * portfolio_weight +
        (mock_interview_score or 0) * interview_weight
    )
    
    return round(score, 2)


def calculate_portfolio_strength(portfolio_count: int) -> float:
    """
    Calculate portfolio strength based on project count.
    Target: 5 projects for full strength (100%).
    """
    return min(portfolio_count / 5 * 100, 100)