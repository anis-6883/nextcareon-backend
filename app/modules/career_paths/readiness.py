"""app/modules/career_paths/readiness.py - Career Readiness Score Calculator."""

from typing import Dict
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.career_paths.models import CareerPath
from app.modules.courses.models import (
    Enrollment, QuizAttempt,
    StudentProjectSubmission
)
from app.modules.portfolio.models import PortfolioProject


WEIGHTS = {
    "course_completion": 0.15,
    "quiz_performance": 0.15,
    "project_quality": 0.30,
    "portfolio_strength": 0.20,
    "mock_interview": 0.20,
}


async def calculate_career_readiness_score(
    session: AsyncSession,
    student_id: str,
    career_path_id: str
) -> Dict:
    path = await session.get(CareerPath, career_path_id)
    if not path:
        return _get_zero_score(career_path_id)
    
    course_completion_score = await _calculate_course_completion_score(session, student_id, path)
    quiz_performance_score = await _calculate_quiz_performance_score(session, student_id, path)
    project_quality_score = await _calculate_project_quality_score(session, student_id, path)
    portfolio_strength_score = await _calculate_portfolio_strength_score(session, student_id)
    mock_interview_score = 0.0
    
    total_score = (
        course_completion_score * WEIGHTS["course_completion"] +
        quiz_performance_score * WEIGHTS["quiz_performance"] +
        project_quality_score * WEIGHTS["project_quality"] +
        portfolio_strength_score * WEIGHTS["portfolio_strength"] +
        mock_interview_score * WEIGHTS["mock_interview"]
    )
    
    return {
        "career_path_id": career_path_id,
        "course_completion_score": round(course_completion_score, 2),
        "quiz_performance_score": round(quiz_performance_score, 2),
        "project_quality_score": round(project_quality_score, 2),
        "portfolio_strength_score": round(portfolio_strength_score, 2),
        "mock_interview_score": round(mock_interview_score, 2),
        "total_score": round(min(100.0, max(0.0, total_score)), 2)
    }


def _get_zero_score(career_path_id: str) -> Dict:
    return {
        "career_path_id": career_path_id,
        "course_completion_score": 0.0,
        "quiz_performance_score": 0.0,
        "project_quality_score": 0.0,
        "portfolio_strength_score": 0.0,
        "mock_interview_score": 0.0,
        "total_score": 0.0
    }


async def _calculate_course_completion_score(
    session: AsyncSession,
    student_id: str,
    path: CareerPath
) -> float:
    if not path.courses:
        return 0.0
    
    total_courses = len(path.courses)
    completed_courses = 0
    
    for path_course in path.courses:
        result = await session.execute(
            select(Enrollment).where(
                Enrollment.student_id == student_id,
                Enrollment.course_id == path_course.course_id
            )
        )
        enrollment = result.first()
        if enrollment and enrollment.completed_at:
            completed_courses += 1
    
    return (completed_courses / total_courses) * 100


async def _calculate_quiz_performance_score(
    session: AsyncSession,
    student_id: str,
    path: CareerPath
) -> float:
    course_ids = [pc.course_id for pc in path.courses]
    if not course_ids:
        return 0.0
    
    result = await session.execute(
        select(QuizAttempt).where(
            QuizAttempt.student_id == student_id
        )
    )
    all_attempts = result.all()
    
    if not all_attempts:
        return 0.0
    
    filtered_attempts = [
        a for a in all_attempts 
        if any(a.quiz_id == qid for qid in 
               select(Course).where(Course.id.in_(course_ids)).columns(Course.id).subquery().columns())
    ]
    
    if not filtered_attempts:
        return 0.0
    
    total_score = sum(a.score for a in filtered_attempts)
    return min(100.0, total_score / len(filtered_attempts))


async def _calculate_project_quality_score(
    session: AsyncSession,
    student_id: str,
    path: CareerPath
) -> float:
    course_ids = [pc.course_id for pc in path.courses]
    if not course_ids:
        return 0.0
    
    result = await session.execute(
        select(StudentProjectSubmission).where(
            StudentProjectSubmission.student_id == student_id
        )
    )
    all_submissions = result.all()
    
    if not all_submissions:
        return 0.0
    
    from app.modules.courses.models import Project
    project_ids = (await session.execute(
        select(Project).where(Project.course_id.in_(course_ids))
    )).all()
    project_id_set = {p.id for p in project_ids}
    
    filtered_submissions = [s for s in all_submissions if s.project_id in project_id_set]
    
    if not filtered_submissions:
        return 0.0
    
    scored_submissions = [s for s in filtered_submissions if s.score is not None]
    if not scored_submissions:
        return 0.0
    
    avg_score = sum(s.score for s in scored_submissions) / len(scored_submissions)
    return min(100.0, avg_score)


async def _calculate_portfolio_strength_score(
    session: AsyncSession,
    student_id: str
) -> float:
    result = await session.execute(
        select(PortfolioProject).where(PortfolioProject.student_id == student_id)
    )
    projects = result.all()
    
    if not projects:
        return 0.0
    
    total_rating = sum(p.quality_rating for p in projects)
    avg_rating = total_rating / len(projects)
    
    return min(100.0, (avg_rating / 5.0) * 100)
