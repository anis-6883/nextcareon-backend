"""app/modules/assignments/router.py - Assignment and Project endpoints."""

from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.modules.assignments.schemas import (
    AssignmentCreate, AssignmentRead, ProjectCreate, ProjectRead,
    AssignmentSubmit, ProjectSubmit, SubmissionRead
)
from app.modules.courses.models import Assignment, Project, StudentAssignmentSubmission, StudentProjectSubmission
from app.db.engine import get_session
from app.core.dependencies import get_current_student, get_current_admin
from app.utils.file_upload import save_student_submission
from typing import List

router = APIRouter(prefix="/assignments", tags=["assignments"])


@router.get("/courses/{course_id}", response_model=List[AssignmentRead])
async def list_assignments(
    course_id: str,
    session: AsyncSession = Depends(get_session),
):
    result = await session.exec(
        select(Assignment).where(Assignment.course_id == course_id)
    )
    return result.all()


@router.post("/", response_model=AssignmentRead, status_code=status.HTTP_201_CREATED)
async def create_assignment(
    assignment: AssignmentCreate,
    session: AsyncSession = Depends(get_session),
    admin=Depends(get_current_admin),
):
    assign = Assignment(**assignment.model_dump())
    session.add(assign)
    await session.commit()
    await session.refresh(assign)
    return assign


@router.post("/{assignment_id}/submit", response_model=SubmissionRead, status_code=status.HTTP_201_CREATED)
async def submit_assignment(
    assignment_id: str,
    submission: AssignmentSubmit,
    session: AsyncSession = Depends(get_session),
    student=Depends(get_current_student),
):
    assign = await session.get(Assignment, assignment_id)
    if not assign:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(resource="Assignment")
    
    sub = StudentAssignmentSubmission(
        student_id=student.id,
        assignment_id=assignment_id,
        submission_url=submission.submission_url,
    )
    session.add(sub)
    await session.commit()
    await session.refresh(sub)
    return sub


@router.post("/{assignment_id}/submit-file", response_model=SubmissionRead, status_code=status.HTTP_201_CREATED)
async def submit_assignment_file(
    assignment_id: str,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    student=Depends(get_current_student),
):
    assign = await session.get(Assignment, assignment_id)
    if not assign:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(resource="Assignment")
    
    url = await save_student_submission(file, student.id, "assignments")
    
    sub = StudentAssignmentSubmission(
        student_id=student.id,
        assignment_id=assignment_id,
        submission_url=url,
    )
    session.add(sub)
    await session.commit()
    await session.refresh(sub)
    return sub


@router.get("/submissions/{assignment_id}", response_model=List[SubmissionRead])
async def get_assignment_submissions(
    assignment_id: str,
    session: AsyncSession = Depends(get_session),
    student=Depends(get_current_student),
):
    result = await session.exec(
        select(StudentAssignmentSubmission).where(
            StudentAssignmentSubmission.assignment_id == assignment_id,
            StudentAssignmentSubmission.student_id == student.id
        )
    )
    return result.all()


@router.get("/projects/courses/{course_id}", response_model=List[ProjectRead])
async def list_projects(
    course_id: str,
    session: AsyncSession = Depends(get_session),
):
    result = await session.exec(
        select(Project).where(Project.course_id == course_id)
    )
    return result.all()


@router.post("/projects", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    session: AsyncSession = Depends(get_session),
    admin=Depends(get_current_admin),
):
    proj = Project(**project.model_dump())
    session.add(proj)
    await session.commit()
    await session.refresh(proj)
    return proj


@router.post("/projects/{project_id}/submit", response_model=SubmissionRead, status_code=status.HTTP_201_CREATED)
async def submit_project(
    project_id: str,
    submission: ProjectSubmit,
    session: AsyncSession = Depends(get_session),
    student=Depends(get_current_student),
):
    proj = await session.get(Project, project_id)
    if not proj:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(resource="Project")
    
    sub = StudentProjectSubmission(
        student_id=student.id,
        project_id=project_id,
        submission_url=submission.submission_url,
    )
    session.add(sub)
    await session.commit()
    await session.refresh(sub)
    return sub


@router.get("/projects/submissions/{project_id}", response_model=List[SubmissionRead])
async def get_project_submissions(
    project_id: str,
    session: AsyncSession = Depends(get_session),
    student=Depends(get_current_student),
):
    result = await session.exec(
        select(StudentProjectSubmission).where(
            StudentProjectSubmission.project_id == project_id,
            StudentProjectSubmission.student_id == student.id
        )
    )
    return result.all()