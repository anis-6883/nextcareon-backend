"""app/modules/career_paths/router.py - Career path endpoints."""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.engine import get_session
from app.modules.career_paths.models import CareerPath, CareerPathCourse, StudentCareerPath
from app.modules.career_paths.schemas import (
    CareerPathRead, CareerPathDetail,
    StudentCareerPathCreate, StudentCareerPathRead,
    CareerReadinessScore
)
from app.modules.career_paths.service import (
    get_career_path_by_slug, get_career_path_by_id,
    enroll_student_in_career_path, calculate_path_completion
)
from app.modules.users.models import Student
from app.core.dependencies import get_current_student
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/career-paths", tags=["career-paths"])


@router.get("/", response_model=List[CareerPathRead])
async def list_career_paths(
    skip: int = 0,
    limit: int = 20,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(CareerPath).offset(skip).limit(limit))
    return result.all()


@router.get("/{path_id}", response_model=CareerPathDetail)
async def get_career_path(
    path_id: str,
    session: AsyncSession = Depends(get_session),
):
    path = await session.get(CareerPath, path_id)
    if not path:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(resource="Career Path")
    
    result = await session.execute(
        select(CareerPathCourse).where(CareerPathCourse.career_path_id == path_id)
    )
    path_course_links = result.all()
    course_ids = [pcl.course_id for pcl in path_course_links]
    
    from app.modules.courses.models import Course
    courses_result = await session.execute(
        select(Course).where(Course.id.in_(course_ids))
    )
    courses = courses_result.all()
    path.courses = list(courses)
    
    return path


@router.post("/enroll/{path_id}", response_model=StudentCareerPathRead, status_code=status.HTTP_201_CREATED)
async def enroll_in_career_path(
    path_id: str,
    student: Student = Depends(get_current_student),
    session: AsyncSession = Depends(get_session),
):
    path = await session.get(CareerPath, path_id)
    if not path:
        raise NotFoundException(resource="Career Path")
    
    enrollment = await enroll_student_in_career_path(
        session, student.id, path_id
    )
    completion_pct = await calculate_path_completion(session, student.id, path_id)
    
    return StudentCareerPathRead(
        id=enrollment.id,
        student_id=enrollment.student_id,
        career_path_id=enrollment.career_path_id,
        status=enrollment.status,
        enrolled_at=enrollment.enrolled_at,
        completion_pct=completion_pct
    )


@router.get("/my-enrollment/{path_id}", response_model=StudentCareerPathRead)
async def get_my_enrollment(
    path_id: str,
    student: Student = Depends(get_current_student),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(StudentCareerPath).where(
            StudentCareerPath.student_id == student.id,
            StudentCareerPath.career_path_id == path_id
        )
    )
    enrollment = result.first()
    if not enrollment:
        raise NotFoundException(resource="Enrollment")
    
    completion_pct = await calculate_path_completion(session, student.id, path_id)
    
    return StudentCareerPathRead(
        id=enrollment.id,
        student_id=enrollment.student_id,
        career_path_id=enrollment.career_path_id,
        status=enrollment.status,
        enrolled_at=enrollment.enrolled_at,
        completion_pct=completion_pct
    )


@router.get("/readiness-score/{path_id}", response_model=CareerReadinessScore)
async def get_career_readiness_score(
    path_id: str,
    student: Student = Depends(get_current_student),
    session: AsyncSession = Depends(get_session),
):
    from app.modules.career_paths.readiness import calculate_career_readiness_score
    return await calculate_career_readiness_score(session, student.id, path_id)
