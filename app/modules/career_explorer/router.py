"""app/modules/career_explorer/router.py - Public Career Explorer endpoints."""

import json
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from redis.asyncio import Redis
from app.db.engine import get_session
from app.cache.redis import get_redis
from app.cache.keys import (
    CAREER_PATHS_LIST, CAREER_PATH_DETAIL,
    CAREER_PATH_MARKET_DATA, JOB_OPENINGS,
    COMPANIES, ALUMNI_SHOWCASE
)
from app.modules.career_paths.models import (
    CareerPath, CareerPathCourse, JobOpening,
    Company, AlumniShowcase, SalaryRange
)
from app.modules.career_paths.schemas import (
    CareerPathRead, CareerPathDetail,
    JobOpeningRead, CompanyRead, AlumniShowcaseRead
)

router = APIRouter(prefix="/career-explorer", tags=["career-explorer"])

CACHE_TTL = 3600


def build_cache_key(base_key: str, params: dict) -> str:
    param_str = "&".join(f"{k}={v}" for k, v in sorted(params.items()) if v is not None)
    return f"{base_key}:{param_str}" if param_str else base_key


@router.get("/paths", response_model=List[CareerPathRead])
async def list_career_paths(
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
):
    cache_key = CAREER_PATHS_LIST
    cached = await redis.get(cache_key)
    if cached:
        return [CareerPathRead.model_validate(cp) for cp in json.loads(cached)]
    
    result = await session.exec(select(CareerPath))
    paths = result.all()
    data = [CareerPathRead.model_validate(p.model_dump()).model_dump() for p in paths]
    await redis.setex(cache_key, CACHE_TTL, json.dumps(data))
    return [CareerPathRead.model_validate(p.model_dump()) for p in paths]


@router.get("/paths/{path_id}", response_model=CareerPathDetail)
async def get_career_path(
    path_id: str,
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
):
    cache_key = CAREER_PATH_DETAIL.format(path_id=path_id)
    cached = await redis.get(cache_key)
    if cached:
        return CareerPathDetail.model_validate(json.loads(cached))
    
    path = await session.get(CareerPath, path_id)
    if not path:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(resource="Career Path")
    
    result = await session.exec(
        select(CareerPathCourse).where(CareerPathCourse.career_path_id == path_id)
    )
    path_course_links = result.all()
    course_ids = [pcl.course_id for pcl in path_course_links]
    
    from app.modules.courses.models import Course
    courses_result = await session.exec(
        select(Course).where(Course.id.in_(course_ids))
    )
    courses = courses_result.all()
    
    path.courses = list(courses)
    
    data = CareerPathDetail.model_validate(path.model_dump()).model_dump()
    await redis.setex(cache_key, CACHE_TTL, json.dumps(data, default=str))
    return CareerPathDetail.model_validate(path.model_dump())


@router.get("/paths/{path_id}/market-data")
async def get_career_path_market_data(
    path_id: str,
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
):
    cache_key = f"{CAREER_PATH_MARKET_DATA}:{path_id}"
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)
    
    from app.modules.career_paths.models import CareerPathMarketData
    result = await session.exec(
        select(CareerPathMarketData).where(CareerPathMarketData.career_path_id == path_id)
    )
    market_data = result.first()
    
    if not market_data:
        return {"career_path_id": path_id, "market_data": None}
    
    data = {"career_path_id": path_id, "market_data": market_data.model_dump()}
    await redis.setex(cache_key, CACHE_TTL, json.dumps(data, default=str))
    return data


@router.get("/jobs", response_model=List[JobOpeningRead])
async def list_job_openings(
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    career_path_id: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
):
    params = {"career_path_id": career_path_id, "location": location}
    cache_key = build_cache_key(JOB_OPENINGS, params)
    cached = await redis.get(cache_key)
    if cached:
        return [JobOpeningRead.model_validate(j) for j in json.loads(cached)]
    
    query = select(JobOpening).where(JobOpening.is_active == True)
    if career_path_id:
        query = query.where(JobOpening.career_path_id == career_path_id)
    result = await session.exec(query)
    openings = result.all()
    
    data = [JobOpeningRead.model_validate(j.model_dump()).model_dump() for j in openings]
    await redis.setex(cache_key, CACHE_TTL, json.dumps(data))
    return [JobOpeningRead.model_validate(j.model_dump()) for j in openings]


@router.get("/companies", response_model=List[CompanyRead])
async def list_companies(
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
):
    cached = await redis.get(COMPANIES)
    if cached:
        return [CompanyRead.model_validate(c) for c in json.loads(cached)]
    
    result = await session.exec(
        select(Company).where(Company.is_active == True)
    )
    companies = result.all()
    data = [CompanyRead.model_validate(c.model_dump()).model_dump() for c in companies]
    await redis.setex(COMPANIES, CACHE_TTL, json.dumps(data))
    return [CompanyRead.model_validate(c.model_dump()) for c in companies]


@router.get("/alumni", response_model=List[AlumniShowcaseRead])
async def list_alumni(
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    career_path_id: Optional[str] = Query(None),
):
    params = {"career_path_id": career_path_id}
    cache_key = build_cache_key(ALUMNI_SHOWCASE, params)
    cached = await redis.get(cache_key)
    if cached:
        return [AlumniShowcaseRead.model_validate(a) for a in json.loads(cached)]
    
    query = select(AlumniShowcase)
    if career_path_id:
        query = query.where(AlumniShowcase.career_path_id == career_path_id)
    result = await session.exec(query)
    alumni = result.all()
    data = [AlumniShowcaseRead.model_validate(a.model_dump()).model_dump() for a in alumni]
    await redis.setex(cache_key, CACHE_TTL, json.dumps(data))
    return [AlumniShowcaseRead.model_validate(a.model_dump()) for a in alumni]


@router.get("/salaries", response_model=List[dict])
async def list_salary_ranges(
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
):
    cache_key = "cache:salary_ranges"
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)
    
    result = await session.exec(select(SalaryRange))
    salary_ranges = result.all()
    data = [sr.model_dump() for sr in salary_ranges]
    await redis.setex(cache_key, CACHE_TTL, json.dumps(data))
    return data