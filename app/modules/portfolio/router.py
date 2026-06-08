"""app/modules/portfolio/router.py - Portfolio endpoints."""

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.engine import get_session
from app.core.dependencies import get_current_student

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_portfolio_project(
    title: str,
    description: str,
    repository_url: str = "",
    live_url: str = "",
    session: AsyncSession = Depends(get_session),
    student=Depends(get_current_student),
):
    """Create a portfolio project."""
    from app.modules.portfolio.models import PortfolioProject
    project = PortfolioProject(
        student_id=str(student.id),
        title=title,
        description=description,
        repository_url=repository_url,
        live_url=live_url,
    )
    session.add(project)
    await session.commit()
    return {"id": project.id}