"""app/modules/career_paths/router.py - Career path endpoints."""

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.engine import get_session

router = APIRouter(prefix="/career-paths", tags=["career-paths"])


@router.get("/")
async def list_career_paths(
    skip: int = 0,
    limit: int = 20,
    session: AsyncSession = Depends(get_session),
):
    """List available career paths."""
    from sqlmodel import select
    from app.modules.career_paths.models import CareerPath
    result = await session.exec(select(CareerPath).offset(skip).limit(limit))
    return result.all()


@router.get("/{path_id}")
async def get_career_path(
    path_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Get career path details with required courses."""
    from app.modules.career_paths.models import CareerPath
    path = await session.get(CareerPath, path_id)
    if not path:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(resource="Career Path")
    return path