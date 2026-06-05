"""app/modules/assignments/router.py - Assignment endpoints."""

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.assignments.schemas import AssignmentRead, ProjectRead, ProjectSubmit
from app.db.engine import get_session
from app.core.dependencies import get_current_student

router = APIRouter(prefix="/assignments", tags=["assignments"])


@router.get("/", response_model=list[AssignmentRead])
async def list_assignments(
    course_id: str,
    session: AsyncSession = Depends(get_session),
):
    """List assignments for a course."""
    from sqlmodel import select
    from app.modules.assignments.models import Assignment
    result = await session.exec(
        select(Assignment).where(Assignment.course_id == course_id)
    )
    return result.all()


@router.post("/{assignment_id}/submit", status_code=status.HTTP_201_CREATED)
async def submit_assignment(
    assignment_id: str,
    data: ProjectSubmit,
    session: AsyncSession = Depends(get_session),
    student=Depends(get_current_student),
):
    """Submit an assignment."""
    from app.modules.assignments.models import Assignment, StudentAssignmentSubmission
    assignment = await session.get(Assignment, assignment_id)
    if not assignment:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(resource="Assignment")
    
    submission = StudentAssignmentSubmission(
        student_id=str(student.id),
        assignment_id=assignment_id,
        submission_url=data.submission_url,
    )
    session.add(submission)
    await session.commit()
    return {"id": submission.id}