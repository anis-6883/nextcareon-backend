"""app/modules/admin/router.py - Admin endpoints."""

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.admin.schemas import AdminLogin, CourseCreate
from app.modules.admin.service import get_admin_by_email
from app.modules.courses.service import create_course
from app.db.engine import get_session
from app.core.security import create_access_token, verify_password

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/login")
async def admin_login(data: AdminLogin, session: AsyncSession = Depends(get_session)):
    """Admin login."""
    admin = await get_admin_by_email(session, data.email)
    if not admin or not verify_password(data.password, admin.password_hash):
        from app.core.exceptions import AuthException
        raise AuthException()
    token = create_access_token(str(admin.id))
    return {"access_token": token, "token_type": "bearer"}


@router.post("/courses", status_code=status.HTTP_201_CREATED)
async def create_course_endpoint(data: CourseCreate, session: AsyncSession = Depends(get_session)):
    """Create a new course (admin only)."""
    from app.modules.admin.schemas import Difficulty
    course = await create_course(
        session,
        title=data.title,
        slug=data.slug,
        description=data.description,
        difficulty=data.difficulty.value if isinstance(data.difficulty, Difficulty) else data.difficulty,
        estimated_hours=data.estimated_hours,
    )
    return {"id": course.id}