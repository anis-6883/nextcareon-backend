"""app/modules/auth/service.py - Authentication business logic."""

from typing import Optional, Tuple
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.users.models import Student, AdminUser
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.exceptions import AuthException
from app.cache.redis import redis_client


async def get_student_by_email(session: AsyncSession, email: str) -> Optional[Student]:
    """Get student by email."""
    result = await session.exec(select(Student).where(Student.email == email))
    return result.first()


async def get_admin_by_email(session: AsyncSession, email: str) -> Optional[AdminUser]:
    """Get admin by email."""
    result = await session.exec(select(AdminUser).where(AdminUser.email == email))
    return result.first()


async def create_student(
    session: AsyncSession,
    full_name: str,
    email: str,
    password: str,
    country: str = "Bangladesh",
) -> Student:
    """Create a new student."""
    student = Student(
        full_name=full_name,
        email=email,
        password_hash=hash_password(password),
        country=country,
    )
    session.add(student)
    await session.commit()
    await session.refresh(student)
    return student


async def create_admin(
    session: AsyncSession,
    full_name: str,
    email: str,
    password: str,
    role: str = "content_manager",
) -> AdminUser:
    """Create a new admin user."""
    from app.modules.users.models import UserRole
    admin_role = UserRole.SUPER_ADMIN if role == "super_admin" else UserRole.CONTENT_MANAGER
    admin = AdminUser(
        full_name=full_name,
        email=email,
        password_hash=hash_password(password),
        role=admin_role,
    )
    session.add(admin)
    await session.commit()
    await session.refresh(admin)
    return admin


async def authenticate_user(
    session: AsyncSession, email: str, password: str
) -> Tuple[str, str]:
    """
    Authenticate a user (student or admin) and return tokens.
    Raises AuthException if credentials are invalid.
    """
    student = await get_student_by_email(session, email)
    if student and verify_password(password, student.password_hash):
        return (
            create_access_token(str(student.id), role="student"),
            create_refresh_token(str(student.id)),
        )

    admin = await get_admin_by_email(session, email)
    if admin and verify_password(password, admin.password_hash):
        return (
            create_access_token(str(admin.id), role="admin"),
            create_refresh_token(str(admin.id)),
        )

    raise AuthException()


async def refresh_access_token(refresh_token: str) -> Tuple[str, str]:
    """
    Validate refresh token and issue new access/refresh tokens.
    Raises AuthException if refresh token is invalid or expired.
    """
    user_id = decode_token(refresh_token)
    if not user_id:
        raise AuthException()

    stored_token = await redis_client.get(f"refresh_token:{user_id}")
    if stored_token != refresh_token:
        raise AuthException()

    return (
        create_access_token(user_id),
        create_refresh_token(user_id),
    )


async def revoke_refresh_token(user_id: str) -> None:
    """Revoke a refresh token on logout."""
    await redis_client.delete(f"refresh_token:{user_id}")