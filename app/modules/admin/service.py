"""app/modules/admin/service.py - Admin business logic."""

from typing import Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.users.models import AdminUser
from app.core.security import hash_password
from app.core.exceptions import NotFoundException, ForbiddenException


async def get_admin_by_email(session: AsyncSession, email: str) -> Optional[AdminUser]:
    """Get admin by email."""
    result = await session.exec(select(AdminUser).where(AdminUser.email == email))
    return result.first()


async def create_admin(
    session: AsyncSession,
    full_name: str,
    email: str,
    password: str,
    role: str = "content_manager",
) -> AdminUser:
    """Create a new admin user."""
    admin = AdminUser(
        full_name=full_name,
        email=email,
        password_hash=hash_password(password),
        role=role,
    )
    session.add(admin)
    await session.commit()
    await session.refresh(admin)
    return admin


async def create_first_admin(session: AsyncSession) -> Optional[AdminUser]:
    """Create the first admin if none exists (for seeding)."""
    result = await session.exec(select(AdminUser))
    if result.first():
        return None
    
    from app.core.config import settings
    return await create_admin(
        session,
        full_name=settings.FIRST_ADMIN_NAME,
        email=settings.FIRST_ADMIN_EMAIL,
        password=settings.FIRST_ADMIN_PASSWORD,
        role="super_admin",
    )