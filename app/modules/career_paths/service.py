"""app/modules/career_paths/service.py - Career path service layer."""

from datetime import datetime
from typing import Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.career_paths.models import (
    CareerPath, CareerPathCourse, StudentCareerPath,
    Company, SalaryRange, JobOpening, AlumniShowcase
)
from app.modules.courses.models import (
    Course, Enrollment, QuizAttempt, 
    StudentAssignmentSubmission, StudentProjectSubmission
)
from app.modules.portfolio.models import PortfolioProject


async def get_career_path_by_slug(session: AsyncSession, slug: str) -> Optional[CareerPath]:
    result = await session.execute(
        select(CareerPath).where(CareerPath.slug == slug)
    )
    return result.first()


async def get_career_path_by_id(session: AsyncSession, path_id: str) -> Optional[CareerPath]:
    return await session.get(CareerPath, path_id)


async def enroll_student_in_career_path(
    session: AsyncSession, 
    student_id: str, 
    career_path_id: str
) -> StudentCareerPath:
    existing = await session.execute(
        select(StudentCareerPath).where(
            StudentCareerPath.student_id == student_id,
            StudentCareerPath.career_path_id == career_path_id
        )
    )
    if existing.first():
        return existing.first()
    
    enrollment = StudentCareerPath(student_id=student_id, career_path_id=career_path_id)
    session.add(enrollment)
    await session.commit()
    await session.refresh(enrollment)
    return enrollment


async def calculate_path_completion(
    session: AsyncSession, 
    student_id: str, 
    career_path_id: str
) -> int:
    path = await session.get(CareerPath, career_path_id)
    if not path:
        return 0
    
    total_courses = len(path.courses)
    if total_courses == 0:
        return 0
    
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
    
    return int((completed_courses / total_courses) * 100)


async def calculate_career_readiness_score(
    session: AsyncSession,
    student_id: str,
    career_path_id: str
) -> dict:
    path = await session.get(CareerPath, career_path_id)
    if not path:
        return {
            "career_path_id": career_path_id,
            "course_completion_score": 0.0,
            "quiz_performance_score": 0.0,
            "project_quality_score": 0.0,
            "portfolio_strength_score": 0.0,
            "mock_interview_score": 0.0,
            "total_score": 0.0
        }
    
    course_completion_score = await calculate_course_completion_score(session, student_id, path)
    quiz_performance_score = await calculate_quiz_performance_score(session, student_id, path)
    project_quality_score = await calculate_project_quality_score(session, student_id, path)
    portfolio_strength_score = await calculate_portfolio_strength_score(session, student_id)
    mock_interview_score = await calculate_mock_interview_score(session, student_id)
    
    total_score = (
        course_completion_score * 0.15 +
        quiz_performance_score * 0.15 +
        project_quality_score * 0.30 +
        portfolio_strength_score * 0.20 +
        mock_interview_score * 0.20
    )
    
    return {
        "career_path_id": career_path_id,
        "course_completion_score": round(course_completion_score, 2),
        "quiz_performance_score": round(quiz_performance_score, 2),
        "project_quality_score": round(project_quality_score, 2),
        "portfolio_strength_score": round(portfolio_strength_score, 2),
        "mock_interview_score": round(mock_interview_score, 2),
        "total_score": round(total_score, 2)
    }


async def calculate_course_completion_score(
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


async def calculate_quiz_performance_score(
    session: AsyncSession, 
    student_id: str, 
    path: CareerPath
) -> float:
    course_ids = [pc.course_id for pc in path.courses]
    if not course_ids:
        return 0.0
    
    result = await session.execute(
        select(QuizAttempt).where(
            QuizAttempt.student_id == student_id,
            QuizAttempt.quiz_id.in_(
                select(Course).where(Course.id.in_(course_ids)).columns(Course.id).subquery()
            )
        )
    )
    attempts = result.all()
    
    if not attempts:
        return 0.0
    
    total_score = sum(a.score for a in attempts)
    return min(100.0, total_score / len(attempts))


async def calculate_project_quality_score(
    session: AsyncSession, 
    student_id: str, 
    path: CareerPath
) -> float:
    course_ids = [pc.course_id for pc in path.courses]
    if not course_ids:
        return 0.0
    
    result = await session.execute(
        select(StudentProjectSubmission).where(
            StudentProjectSubmission.student_id == student_id,
            StudentProjectSubmission.project_id.in_(
                select(Course).where(Course.id.in_(course_ids)).columns(Course.id).subquery()
            )
        )
    )
    submissions = result.all()
    
    if not submissions:
        return 0.0
    
    scored_submissions = [s for s in submissions if s.score is not None]
    if not scored_submissions:
        return 0.0
    
    avg_score = sum(s.score for s in scored_submissions) / len(scored_submissions)
    return min(100.0, avg_score)


async def calculate_portfolio_strength_score(
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


async def calculate_mock_interview_score(
    session: AsyncSession, 
    student_id: str
) -> float:
    return 0.0


async def create_company(session: AsyncSession, **kwargs) -> Company:
    company = Company(**kwargs)
    session.add(company)
    await session.commit()
    await session.refresh(company)
    return company


async def get_company_by_id(session: AsyncSession, company_id: str) -> Optional[Company]:
    return await session.get(Company, company_id)


async def get_company_by_name(session: AsyncSession, name: str) -> Optional[Company]:
    result = await session.execute(select(Company).where(Company.name == name))
    return result.first()


async def create_salary_range(session: AsyncSession, **kwargs) -> SalaryRange:
    salary_range = SalaryRange(**kwargs)
    session.add(salary_range)
    await session.commit()
    await session.refresh(salary_range)
    return salary_range


async def get_salary_range_by_career_path(
    session: AsyncSession, 
    career_path_id: str
) -> Optional[SalaryRange]:
    result = await session.execute(
        select(SalaryRange).where(SalaryRange.career_path_id == career_path_id)
    )
    return result.first()


async def create_job_opening(session: AsyncSession, **kwargs) -> JobOpening:
    job_opening = JobOpening(**kwargs)
    session.add(job_opening)
    await session.commit()
    await session.refresh(job_opening)
    return job_opening


async def get_job_opening_by_id(
    session: AsyncSession, 
    job_opening_id: str
) -> Optional[JobOpening]:
    return await session.get(JobOpening, job_opening_id)


async def create_alumni_showcase(session: AsyncSession, **kwargs) -> AlumniShowcase:
    alumni = AlumniShowcase(**kwargs)
    session.add(alumni)
    await session.commit()
    await session.refresh(alumni)
    return alumni


async def get_alumni_by_id(session: AsyncSession, alumni_id: str) -> Optional[AlumniShowcase]:
    return await session.get(AlumniShowcase, alumni_id)
