"""app/modules/career_score/router.py - Career score API endpoints."""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.engine import get_session
from app.modules.career_score.schemas import (
    ScoreOverrideRequest,
    StudentPublicProfileResponse,
    ScoreTimelineResponse,
    StudentRankingResponse,
)
from app.modules.career_score.service import (
    recalculate_student_score,
    get_student_public_profile,
    get_score_timeline,
    get_student_ranking,
    create_score_override,
)
from app.modules.users.models import Student, AdminUser
from app.modules.career_score.models import CareerScore
from app.core.dependencies import get_current_admin

router = APIRouter()


@router.get("/students/{username}/profile", response_model=StudentPublicProfileResponse)
async def get_public_profile(username: str):
    """Get public profile for a student by username/email."""
    async with get_session() as session:
        student = (await session.execute(
            select(Student).where(Student.email == username)
        )).first()
        
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        profile = await get_student_public_profile(student.id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        return profile


@router.get("/students/{student_id}/score-timeline", response_model=ScoreTimelineResponse)
async def get_score_timeline_endpoint(student_id: str, session: AsyncSession = Depends(get_session)):
    """Get score timeline for a student."""
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    timeline = await get_score_timeline(student_id)
    return ScoreTimelineResponse(student_id=student_id, timeline=timeline)


@router.get("/students/{student_id}/ranking", response_model=StudentRankingResponse)
async def get_student_ranking_endpoint(student_id: str, session: AsyncSession = Depends(get_session)):
    """Get student's ranking and percentile."""
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    ranking = await get_student_ranking(student_id)
    return StudentRankingResponse(
        student_id=student_id,
        rank=ranking["rank"],
        percentile=ranking["percentile"],
        total_students=ranking["total_students"],
    )


@router.post("/admin/scores/override")
async def override_score(
    request: ScoreOverrideRequest,
    current_admin: Annotated[AdminUser, Depends(get_current_admin)],
    session: AsyncSession = Depends(get_session),
):
    """Admin endpoint to override a student's score metric."""
    student = session.get(Student, request.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    career_score = (await session.execute(
        select(CareerScore).where(CareerScore.student_id == request.student_id)
    )).first()
    
    if not career_score:
        raise HTTPException(status_code=404, detail="Career score not found for student")
    
    old_value = getattr(career_score, f"{request.metric.value.lower()}_score", 0)
    
    setattr(career_score, f"{request.metric.value.lower()}_score", request.new_value)
    await session.commit()
    await session.refresh(career_score)
    
    await create_score_override(
        student_id=request.student_id,
        admin_id=current_admin.id,
        metric=request.metric,
        old_value=old_value,
        new_value=request.new_value,
        reason=request.reason,
    )
    
    return {"message": "Score override recorded", "new_value": request.new_value}


@router.post("/students/{student_id}/recalculate")
async def trigger_recalculation(student_id: str):
    """Trigger background score recalculation for a student."""
    import asyncio
    asyncio.create_task(recalculate_student_score(student_id))
    return {"message": "Score recalculation triggered"}
