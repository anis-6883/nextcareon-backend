"""app/modules/auth/router.py - Authentication endpoints."""

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.auth.schemas import StudentSignup, AdminSignup, UserLogin, Token, RefreshToken, MessageResponse
from app.modules.auth.service import (
    create_student,
    create_admin,
    authenticate_user,
    refresh_access_token,
    revoke_refresh_token,
)
from app.db.engine import get_session
from app.core.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/student/signup", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def student_signup(data: StudentSignup, session: AsyncSession = Depends(get_session)):
    """Register a new student."""
    from app.modules.auth.service import get_student_by_email
    existing = await get_student_by_email(session, data.email)
    if existing:
        from app.core.exceptions import BadRequestException
        raise BadRequestException(detail="Email already registered")
    await create_student(
        session,
        full_name=data.full_name,
        email=data.email,
        password=data.password,
        country=data.country,
    )
    return MessageResponse(message="Student registered successfully")


@router.post("/admin/signup", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def admin_signup(data: AdminSignup, session: AsyncSession = Depends(get_session)):
    """Register a new admin user."""
    from app.modules.auth.service import get_admin_by_email
    existing = await get_admin_by_email(session, data.email)
    if existing:
        from app.core.exceptions import BadRequestException
        raise BadRequestException(detail="Email already registered")
    await create_admin(
        session,
        full_name=data.full_name,
        email=data.email,
        password=data.password,
        role="content_manager",
    )
    return MessageResponse(message="Admin registered successfully")


@router.post("/login", response_model=Token)
async def login(data: UserLogin, session: AsyncSession = Depends(get_session)):
    """Login endpoint for both students and admins."""
    access_token, refresh_token = await authenticate_user(
        session, data.email, data.password
    )
    user_id = decode_token(access_token)
    if user_id:
        from app.core.security import store_refresh_token
        await store_refresh_token(user_id, refresh_token)
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token)
async def refresh(data: RefreshToken):
    """Refresh access token using refresh token."""
    access_token, new_refresh_token = await refresh_access_token(data.refresh_token)
    return Token(access_token=access_token, refresh_token=new_refresh_token)


@router.post("/logout", response_model=MessageResponse)
async def logout(token: str = Depends(oauth2_scheme)):
    """Logout and revoke refresh token."""
    user_id = decode_token(token)
    if user_id:
        await revoke_refresh_token(user_id)
    return MessageResponse(message="Logged out successfully")