"""app/core/dependencies.py - FastAPI dependency injections."""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.engine import get_session
from app.core.security import decode_token
from app.modules.users.models import Student
from app.core.exceptions import AuthException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")


async def get_current_student(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> Student:
    """Extract and validate current student from JWT token."""
    student_id = decode_token(token)
    if not student_id:
        raise AuthException()
    result = await session.exec(
        select(Student).where(Student.id == student_id)
    )
    student = result.first()
    if not student:
        raise AuthException()
    return student


# Import select at module level
from sqlmodel import select