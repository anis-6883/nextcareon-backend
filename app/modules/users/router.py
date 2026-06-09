"""app/modules/users/router.py - User endpoints."""

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.users.schemas import StudentRead, StudentSignup, Token, UserLogin
from app.modules.users.service import get_student_by_email, get_student_by_id, create_student
from app.db.engine import get_session
from app.core.security import create_access_token, verify_password, create_refresh_token
from app.core.exceptions import AuthException, BadRequestException

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=StudentRead)
async def get_current_student_profile(
    session: AsyncSession = Depends(get_session),
):
    """Get current student profile (requires JWT)."""
    from app.core.dependencies import get_current_student
    return await get_current_student_profile_dependency(session)


async def get_current_student_profile_dependency(
    session: AsyncSession,
):
    """Placeholder for dependency injection - use get_current_student from dependencies."""
    pass


@router.post("/signup", response_model=StudentRead, status_code=status.HTTP_201_CREATED)
async def signup(data: StudentSignup, session: AsyncSession = Depends(get_session)):
    """Register a new student."""
    existing = await get_student_by_email(session, data.email)
    if existing:
        raise BadRequestException(detail="Email already registered")
    student = await create_student(
        session,
        full_name=data.full_name,
        email=data.email,
        password=data.password,
        country=data.country,
    )
    return StudentRead.model_validate(student)


@router.post("/login", response_model=Token)
async def login(data: UserLogin, session: AsyncSession = Depends(get_session)):
    """Login and get JWT tokens."""
    student = await get_student_by_email(session, data.email)
    if not student or not verify_password(data.password, student.password_hash):
        raise AuthException()
    return Token(
        access_token=create_access_token(str(student.id), role="student"),
        refresh_token=create_refresh_token(str(student.id)),
    )
