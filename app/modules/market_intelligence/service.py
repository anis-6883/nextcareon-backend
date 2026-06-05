"""app/modules/market_intelligence/service.py - Market data service."""

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.career_paths.models import CareerPath, CareerPathCompany, CareerPathJobOpening


async def get_companies_for_path(session: AsyncSession, path_id: str):
    """Get companies hiring for a career path."""
    result = await session.exec(
        select(CareerPathCompany).where(CareerPathCompany.career_path_id == path_id)
    )
    return result.all()


async def get_jobs_for_path(session: AsyncSession, path_id: str, location: str = "Bangladesh"):
    """Get job openings for a career path."""
    result = await session.exec(
        select(CareerPathJobOpening)
        .where(
            CareerPathJobOpening.career_path_id == path_id,
            CareerPathJobOpening.location.contains(location),
        )
    )
    return result.all()


async def get_alumni_for_path(session: AsyncSession, path_id: str):
    """Get alumni featured for a career path."""
    result = await session.exec(
        select(CareerPath).where(CareerPath.id == path_id)
    )
    path = result.first()
    if path:
        return path.alumni
    return []