"""app/core/dependencies.py - FastAPI dependency injections."""

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.engine import get_session
from app.core.security import decode_token_with_role
from app.modules.users.models import Student, AdminUser, UserRole
from app.core.exceptions import AuthException, ForbiddenException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Extract and validate current user from JWT token. Returns user info dict."""
    payload = decode_token_with_role(token)
    if not payload:
        raise AuthException()
    return payload


async def get_current_student(
    user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Student:
    """Extract and validate current student from JWT token."""
    if user.get("role") != "student":
        raise ForbiddenException(detail="Student access required")

    result = await session.execute(select(Student).where(Student.id == user.get("sub")))
    student = result.first()
    if not student:
        raise AuthException()
    return student


async def get_current_admin(
    user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> AdminUser:
    """Extract and validate current admin from JWT token."""
    if user.get("role") != "admin":
        raise ForbiddenException(detail="Admin access required")

    result = await session.execute(select(AdminUser).where(AdminUser.id == user.get("sub")))
    admin = result.first()
    if not admin:
        raise AuthException()
    return admin


async def get_super_admin(
    admin: AdminUser = Depends(get_current_admin),
) -> AdminUser:
    """Validate that current admin is a super admin."""
    if admin.role != UserRole.SUPER_ADMIN:
        raise ForbiddenException(detail="Super admin access required")
    return admin
