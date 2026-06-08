"""app/modules/career_score/service.py - Career score computation and management service."""

from datetime import datetime
from typing import Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.career_score.models import (
    CareerScore,
    CareerScoreHistory,
    AdminScoreOverrideAuditLog,
    MockInterviewCredit,
    MetricType,
    StudentCourseProgress,
)
from app.modules.users.models import Student
from app.modules.courses.models import QuizAttempt, StudentProjectSubmission
from app.modules.portfolio.models import PortfolioProject
from app.modules.career_score.calculator import (
    calculate_career_readiness_score,
)
from app.cache.redis import redis_client
from app.db.engine import engine


async def get_course_completion_score(session: AsyncSession, student_id: str) -> float:
    """Calculate course completion score (0-100)."""
    progress_records = (await session.exec(
        select(StudentCourseProgress).where(StudentCourseProgress.student_id == student_id)
    )).all()
    
    if not progress_records:
        return 0.0
    
    total_progress = sum(r.completion_pct for r in progress_records)
    total_possible = len(progress_records) * 100
    
    return round((total_progress / total_possible) * 100, 2) if total_possible > 0 else 0.0


async def get_quiz_performance_score(session: AsyncSession, student_id: str) -> float:
    """Calculate average quiz performance score (0-100)."""
    attempts = (await session.exec(
        select(QuizAttempt).where(QuizAttempt.student_id == student_id)
    )).all()
    
    if not attempts:
        return 0.0
    
    scores = [a.score for a in attempts if a.score is not None]
    return round(sum(scores) / len(scores), 2) if scores else 0.0


async def get_project_quality_score(session: AsyncSession, student_id: str) -> float:
    """Calculate average project quality score (0-100)."""
    submissions = (await session.exec(
        select(StudentProjectSubmission).where(
            StudentProjectSubmission.student_id == student_id,
            StudentProjectSubmission.score.isnot(None)
        )
    )).all()
    
    if not submissions:
        return 0.0
    
    scores = [s.score for s in submissions]
    return round(sum(scores) / len(scores), 2) if scores else 0.0


async def get_portfolio_strength_score(session: AsyncSession, student_id: str) -> float:
    """Calculate portfolio strength score based on reviewed projects."""
    projects = (await session.exec(
        select(PortfolioProject).where(
            PortfolioProject.student_id == student_id,
            PortfolioProject.admin_quality_rating.isnot(None)
        )
    )).all()
    
    if not projects:
        return 0.0
    
    ratings = [p.admin_quality_rating for p in projects if p.admin_quality_rating is not None]
    return round(sum(ratings) / len(ratings), 2) if ratings else 0.0


async def get_mock_interview_score(session: AsyncSession, student_id: str) -> float:
    """Get the best mock interview score (0-100)."""
    credits = await session.exec(
        select(MockInterviewCredit).where(MockInterviewCredit.student_id == student_id)
    ).first()
    
    if not credits or credits.available_credits == 0:
        return 0.0
    
    return 0.0


async def recalculate_student_score(student_id: str) -> CareerScore:
    """
    Recalculate and update a student's career score.
    This is the main entry point for background workers.
    """
    async with AsyncSession(engine) as session:
        course_score = await get_course_completion_score(session, student_id)
        quiz_score = await get_quiz_performance_score(session, student_id)
        project_score = await get_project_quality_score(session, student_id)
        portfolio_score = await get_portfolio_strength_score(session, student_id)
        interview_score = await get_mock_interview_score(session, student_id)
        
        total_score = calculate_career_readiness_score(
            course_score,
            quiz_score,
            project_score,
            portfolio_score,
            interview_score,
        )
        
        career_score = (await session.exec(
            select(CareerScore).where(CareerScore.student_id == student_id)
        )).first()
        
        if not career_score:
            career_score = CareerScore(student_id=student_id)
            session.add(career_score)
        
        old_total = career_score.total_career_score
        
        career_score.course_completion_score = course_score
        career_score.quiz_performance_score = quiz_score
        career_score.project_quality_score = project_score
        career_score.portfolio_strength_score = portfolio_score
        career_score.mock_interview_score = interview_score
        career_score.total_career_score = total_score
        career_score.last_calculated_at = datetime.utcnow()
        
        await session.commit()
        await session.refresh(career_score)
        
        if old_total != total_score:
            history = CareerScoreHistory(
                student_id=student_id,
                total_career_score=total_score,
            )
            session.add(history)
            await session.commit()
        
        await update_leaderboard_cache(student_id, total_score)
        
        return career_score


async def update_leaderboard_cache(student_id: str, score: float):
    """Update Redis sorted set for leaderboard ranking."""
    await redis_client.zadd("career_score_leaderboard", {student_id: score})


async def get_student_ranking(student_id: str) -> dict:
    """Get student's ranking and percentile."""
    async with AsyncSession(engine) as session:
        career_score = (await session.exec(
            select(CareerScore).where(CareerScore.student_id == student_id)
        )).first()
        
        if not career_score:
            return {"rank": 0, "percentile": 0, "total_students": 0}
        
        total = await redis_client.zcount("career_score_leaderboard", "-inf", "+inf")
        score = await redis_client.zscore("career_score_leaderboard", student_id)
        
        if score is None:
            score = career_score.total_career_score
            await redis_client.zadd("career_score_leaderboard", {student_id: score})
        
        rank = await redis_client.zrevrank("career_score_leaderboard", student_id)
        rank = rank + 1 if rank is not None else 1
        
        percentile = round((1 - rank / total) * 100, 2) if total > 0 else 0
        
        return {
            "rank": rank,
            "percentile": percentile,
            "total_students": total,
        }


async def get_student_public_profile(student_id: str) -> dict:
    """Get public profile data for a student."""
    async with AsyncSession(engine) as session:
        student = session.get(Student, student_id)
        if not student:
            return None
        
        career_score = (await session.exec(
            select(CareerScore).where(CareerScore.student_id == student_id)
        )).first()
        
        projects = (await session.exec(
            select(PortfolioProject).where(
                PortfolioProject.student_id == student_id,
                PortfolioProject.admin_quality_rating.isnot(None)
            )
        )).all()
        
        return {
            "student_id": student.id,
            "full_name": student.full_name,
            "dream_career": student.dream_career,
            "education_level": student.education_level,
            "experience_level": student.experience_level,
            "career_score": {
                "total": career_score.total_career_score if career_score else 0,
                "breakdown": {
                    "course_completion": career_score.course_completion_score if career_score else 0,
                    "quiz_performance": career_score.quiz_performance_score if career_score else 0,
                    "project_quality": career_score.project_quality_score if career_score else 0,
                    "portfolio_strength": career_score.portfolio_strength_score if career_score else 0,
                    "mock_interview": career_score.mock_interview_score if career_score else 0,
                } if career_score else {},
            },
            "portfolio_projects": [
                {
                    "title": p.title,
                    "repository_url": p.repository_url,
                    "live_url": p.live_url,
                    "admin_quality_rating": p.admin_quality_rating,
                }
                for p in projects
            ],
        }


async def get_score_timeline(student_id: str) -> list:
    """Get historical score timeline."""
    async with AsyncSession(engine) as session:
        history = (await session.exec(
            select(CareerScoreHistory)
            .where(CareerScoreHistory.student_id == student_id)
            .order_by(CareerScoreHistory.recorded_at)
        )).all()
        
        return [
            {
                "score": h.total_career_score,
                "recorded_at": h.recorded_at.isoformat(),
            }
            for h in history
        ]


async def create_score_override(
    student_id: str,
    admin_id: str,
    metric: MetricType,
    old_value: float,
    new_value: float,
    reason: str,
) -> AdminScoreOverrideAuditLog:
    """Create an audit log entry for a score override."""
    async with AsyncSession(engine) as session:
        audit_log = AdminScoreOverrideAuditLog(
            student_id=student_id,
            admin_id=admin_id,
            metric_changed=metric,
            old_value=old_value,
            new_value=new_value,
            reason_for_override=reason,
        )
        session.add(audit_log)
        await session.commit()
        await session.refresh(audit_log)
        return audit_log