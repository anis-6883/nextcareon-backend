"""app/modules/admin/router.py - Admin endpoints."""

from typing import List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.admin.schemas import (
    AdminLogin,
    StudentRead,
    StudentUpdate,
    AdminUserRead,
    AdminUserCreate,
)
from app.modules.admin.service import get_admin_by_email, create_admin
from app.modules.admin.market_intelligence.router import router as market_intelligence_router
from app.modules.users.models import Student, AdminUser
from app.modules.users.service import get_student_by_id
from app.db.engine import get_session
from app.core.security import create_access_token, verify_password
from app.core.dependencies import get_current_admin, get_super_admin
from app.core.exceptions import AuthException, BadRequestException


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


router = APIRouter(prefix="/admin", tags=["admin"])
router.include_router(market_intelligence_router)


@router.post("/login", response_model=Token)
async def admin_login(data: AdminLogin, session: AsyncSession = Depends(get_session)):
    """Admin login endpoint."""
    admin = await get_admin_by_email(session, data.email)
    if not admin or not verify_password(data.password, admin.password_hash):
        raise AuthException()
    token = create_access_token(str(admin.id), role="admin")
    return Token(access_token=token, refresh_token="", token_type="bearer")


@router.get("/students", response_model=List[StudentRead])
async def list_students(
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """List all students (admin only)."""
    result = await session.execute(select(Student))
    students = result.all()
    return [StudentRead.model_validate(s.model_dump()) for s in students]


@router.get("/students/{student_id}", response_model=StudentRead)
async def get_student(
    student_id: str,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Get a student by ID (admin only)."""
    student = await get_student_by_id(session, student_id)
    return StudentRead.model_validate(student.model_dump())


@router.patch("/students/{student_id}", response_model=StudentRead)
async def update_student(
    student_id: str,
    data: StudentUpdate,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Update a student (admin only)."""
    student = await get_student_by_id(session, student_id)
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(student, field, value)
    await session.commit()
    await session.refresh(student)
    return StudentRead.model_validate(student.model_dump())


@router.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(
    student_id: str,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_super_admin),
):
    """Delete a student (super admin only)."""
    student = await get_student_by_id(session, student_id)
    await session.delete(student)
    await session.commit()


@router.post("/admins", response_model=AdminUserRead, status_code=status.HTTP_201_CREATED)
async def create_admin_user(
    data: AdminUserCreate,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_super_admin),
):
    """Create a new admin user (super admin only)."""
    existing = await get_admin_by_email(session, data.email)
    if existing:
        raise BadRequestException(detail="Email already registered")
    new_admin = await create_admin(
        session,
        full_name=data.full_name,
        email=data.email,
        password=data.password,
        role=data.role,
    )
    return AdminUserRead.model_validate(new_admin.model_dump())
