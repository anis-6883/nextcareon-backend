"""app/modules/users/service.py - User business logic."""

from typing import Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.users.models import Student, AdminUser
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.core.exceptions import NotFoundException, AuthException


async def get_student_by_email(session: AsyncSession, email: str) -> Optional[Student]:
    """Get student by email."""
    result = await session.execute(select(Student).where(Student.email == email))
    return result.first()


async def get_student_by_id(session: AsyncSession, student_id: str) -> Student:
    """Get student by ID or raise 404."""
    student = await session.get(Student, student_id)
    if not student:
        raise NotFoundException(resource="Student")
    return student


async def get_admin_by_email(session: AsyncSession, email: str) -> Optional[AdminUser]:
    """Get admin by email."""
    result = await session.execute(select(AdminUser).where(AdminUser.email == email))
    return result.first()


async def create_student(session: AsyncSession, full_name: str, email: str, password: str, **kwargs) -> Student:
    """Create a new student."""
    student = Student(
        full_name=full_name,
        email=email,
        password_hash=hash_password(password),
        **kwargs
    )
    session.add(student)
    await session.commit()
    await session.refresh(student)
    return student


async def authenticate_student(session: AsyncSession, email: str, password: str) -> tuple[str, str]:
    """Authenticate student and return tokens."""
    student = await get_student_by_email(session, email)
    if not student or not verify_password(password, student.password_hash):
        raise AuthException()
    return (
        create_access_token(str(student.id)),
        create_refresh_token(str(student.id)),
    )


async def update_student_xp(session: AsyncSession, student_id: str, xp: int, coins: int) -> Student:
    """Update student XP and coins."""
    student = await get_student_by_id(session, student_id)
    student.xp_points += xp
    student.coins += coins
    await session.commit()
    await session.refresh(student)
    return student
