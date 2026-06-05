"""app/modules/users/router.py - User authentication endpoints."""

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.users.schemas import StudentSignup, StudentRead, Token, UserLogin
from app.modules.users.service import get_student_by_email, create_student, authenticate_student
from app.db.engine import get_session

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/signup", response_model=StudentRead, status_code=status.HTTP_201_CREATED)
async def signup(data: StudentSignup, session: AsyncSession = Depends(get_session)):
    """Register a new student."""
    existing = await get_student_by_email(session, data.email)
    if existing:
        from app.core.exceptions import BadRequestException
        raise BadRequestException(detail="Email already registered")
    student = await create_student(
        session,
        full_name=data.full_name,
        email=data.email,
        password=data.password,
        country=data.country,
        education_level=data.education_level,
        experience_level=data.experience_level,
        dream_career=data.dream_career,
    )
    return StudentRead.model_validate(student)


@router.post("/login", response_model=Token)
async def login(data: UserLogin, session: AsyncSession = Depends(get_session)):
    """Login and get JWT tokens."""
    access, refresh = await authenticate_student(session, data.email, data.password)
    return Token(access_token=access, refresh_token=refresh)