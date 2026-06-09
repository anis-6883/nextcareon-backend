"""app/modules/admin/market_intelligence/router.py - Admin Market Intelligence endpoints."""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.engine import get_session
from app.cache.decorators import invalidate_career_explorer_cache
from app.modules.career_paths.models import Company, SalaryRange, JobOpening, AlumniShowcase
from app.modules.career_paths.schemas import (
    CompanyCreate, CompanyRead,
    SalaryRangeCreate, SalaryRangeRead,
    JobOpeningCreate, JobOpeningRead,
    AlumniShowcaseCreate, AlumniShowcaseRead,
)
from app.modules.career_paths.service import (
    create_company, get_company_by_id,
    create_salary_range, get_salary_range_by_career_path,
    create_job_opening, get_job_opening_by_id,
    create_alumni_showcase, get_alumni_by_id,
)
from app.modules.users.models import AdminUser
from app.core.dependencies import get_current_admin
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/api/v1/admin/market-intelligence", tags=["admin-market-intelligence"])


@router.post("/companies", response_model=CompanyRead, status_code=status.HTTP_201_CREATED)
async def create_company_endpoint(
    data: CompanyCreate,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    existing = await session.execute(
        session.query(Company).where(Company.name == data.name)
    ) if (company := await get_company_by_id(session, data.name)) else None
    
    company = await create_company(session, **data.model_dump())
    await invalidate_career_explorer_cache()
    return company


@router.get("/companies", response_model=List[CompanyRead])
async def list_companies(
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    from sqlmodel import select
    from app.modules.career_paths.models import Company
    result = await session.execute(select(Company))
    return result.all()


@router.get("/companies/{company_id}", response_model=CompanyRead)
async def get_company_endpoint(
    company_id: str,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    from app.modules.career_paths.models import Company
    company = await session.get(Company, company_id)
    if not company:
        raise NotFoundException(resource="Company")
    return company


@router.put("/companies/{company_id}", response_model=CompanyRead)
async def update_company_endpoint(
    company_id: str,
    data: CompanyCreate,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    from app.modules.career_paths.models import Company
    company = await session.get(Company, company_id)
    if not company:
        raise NotFoundException(resource="Company")
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(company, field, value)
    await session.commit()
    await session.refresh(company)
    await invalidate_career_explorer_cache()
    return company


@router.delete("/companies/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company_endpoint(
    company_id: str,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    from app.modules.career_paths.models import Company
    company = await session.get(Company, company_id)
    if not company:
        raise NotFoundException(resource="Company")
    await session.delete(company)
    await session.commit()
    await invalidate_career_explorer_cache()


@router.post("/salary-ranges", response_model=SalaryRangeRead, status_code=status.HTTP_201_CREATED)
async def create_salary_range_endpoint(
    data: SalaryRangeCreate,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    salary_range = await create_salary_range(session, **data.model_dump())
    await invalidate_career_explorer_cache()
    return salary_range


@router.get("/salary-ranges", response_model=List[SalaryRangeRead])
async def list_salary_ranges(
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    from sqlmodel import select
    from app.modules.career_paths.models import SalaryRange
    result = await session.execute(select(SalaryRange))
    return result.all()


@router.get("/salary-ranges/career-path/{career_path_id}", response_model=SalaryRangeRead)
async def get_salary_range_by_path(
    career_path_id: str,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    salary_range = await get_salary_range_by_career_path(session, career_path_id)
    if not salary_range:
        raise NotFoundException(resource="Salary Range")
    return salary_range


@router.put("/salary-ranges/{salary_range_id}", response_model=SalaryRangeRead)
async def update_salary_range_endpoint(
    salary_range_id: str,
    data: SalaryRangeCreate,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    from app.modules.career_paths.models import SalaryRange
    salary_range = await session.get(SalaryRange, salary_range_id)
    if not salary_range:
        raise NotFoundException(resource="Salary Range")
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(salary_range, field, value)
    await session.commit()
    await session.refresh(salary_range)
    await invalidate_career_explorer_cache()
    return salary_range


@router.delete("/salary-ranges/{salary_range_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_salary_range_endpoint(
    salary_range_id: str,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    from app.modules.career_paths.models import SalaryRange
    salary_range = await session.get(SalaryRange, salary_range_id)
    if not salary_range:
        raise NotFoundException(resource="Salary Range")
    await session.delete(salary_range)
    await session.commit()
    await invalidate_career_explorer_cache()


@router.post("/job-openings", response_model=JobOpeningRead, status_code=status.HTTP_201_CREATED)
async def create_job_opening_endpoint(
    data: JobOpeningCreate,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    job_opening = await create_job_opening(session, **data.model_dump())
    await invalidate_career_explorer_cache()
    return job_opening


@router.get("/job-openings", response_model=List[JobOpeningRead])
async def list_job_openings(
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    from sqlmodel import select
    from app.modules.career_paths.models import JobOpening
    result = await session.execute(select(JobOpening))
    return result.all()


@router.get("/job-openings/{job_opening_id}", response_model=JobOpeningRead)
async def get_job_opening_endpoint(
    job_opening_id: str,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    job_opening = await get_job_opening_by_id(session, job_opening_id)
    if not job_opening:
        raise NotFoundException(resource="Job Opening")
    return job_opening


@router.put("/job-openings/{job_opening_id}", response_model=JobOpeningRead)
async def update_job_opening_endpoint(
    job_opening_id: str,
    data: JobOpeningCreate,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    from app.modules.career_paths.models import JobOpening
    job_opening = await session.get(JobOpening, job_opening_id)
    if not job_opening:
        raise NotFoundException(resource="Job Opening")
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job_opening, field, value)
    await session.commit()
    await session.refresh(job_opening)
    await invalidate_career_explorer_cache()
    return job_opening


@router.delete("/job-openings/{job_opening_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job_opening_endpoint(
    job_opening_id: str,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    from app.modules.career_paths.models import JobOpening
    job_opening = await session.get(JobOpening, job_opening_id)
    if not job_opening:
        raise NotFoundException(resource="Job Opening")
    await session.delete(job_opening)
    await session.commit()
    await invalidate_career_explorer_cache()


@router.post("/alumni", response_model=AlumniShowcaseRead, status_code=status.HTTP_201_CREATED)
async def create_alumni_endpoint(
    data: AlumniShowcaseCreate,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    alumni = await create_alumni_showcase(session, **data.model_dump())
    await invalidate_career_explorer_cache()
    return alumni


@router.get("/alumni", response_model=List[AlumniShowcaseRead])
async def list_alumni(
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    from sqlmodel import select
    from app.modules.career_paths.models import AlumniShowcase
    result = await session.execute(select(AlumniShowcase))
    return result.all()


@router.get("/alumni/{alumni_id}", response_model=AlumniShowcaseRead)
async def get_alumni_endpoint(
    alumni_id: str,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    alumni = await get_alumni_by_id(session, alumni_id)
    if not alumni:
        raise NotFoundException(resource="Alumni")
    return alumni


@router.put("/alumni/{alumni_id}", response_model=AlumniShowcaseRead)
async def update_alumni_endpoint(
    alumni_id: str,
    data: AlumniShowcaseCreate,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    from app.modules.career_paths.models import AlumniShowcase
    alumni = await session.get(AlumniShowcase, alumni_id)
    if not alumni:
        raise NotFoundException(resource="Alumni")
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(alumni, field, value)
    await session.commit()
    await session.refresh(alumni)
    await invalidate_career_explorer_cache()
    return alumni


@router.delete("/alumni/{alumni_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alumni_endpoint(
    alumni_id: str,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    from app.modules.career_paths.models import AlumniShowcase
    alumni = await session.get(AlumniShowcase, alumni_id)
    if not alumni:
        raise NotFoundException(resource="Alumni")
    await session.delete(alumni)
    await session.commit()
    await invalidate_career_explorer_cache()
