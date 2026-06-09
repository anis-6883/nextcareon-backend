"""app/modules/career_paths/schemas.py - Pydantic schemas for career paths."""

from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field
from app.modules.courses.schemas import CourseRead


class CareerPathDifficulty(str, Enum):
    """Career path difficulty."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class CareerPathStatus(str, Enum):
    """Student career path enrollment status."""
    ENROLLED = "enrolled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class CareerPathBase(BaseModel):
    title: str = Field(max_length=255)
    slug: str = Field(max_length=255)
    description: str = Field(default="")
    difficulty: CareerPathDifficulty = CareerPathDifficulty.MEDIUM
    estimated_hours: int = Field(default=0, ge=0)


class CareerPathCreate(CareerPathBase):
    course_ids: List[str] = Field(default=[])


class CareerPathRead(CareerPathBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class CareerPathDetail(CareerPathRead):
    courses: List[CourseRead] = Field(default=[])

    class Config:
        from_attributes = True


class CareerPathCourseBase(BaseModel):
    course_id: str
    order_index: int


class CareerPathCourseCreate(CareerPathCourseBase):
    pass


class CareerPathCourseRead(CareerPathCourseBase):
    id: str
    career_path_id: str

    class Config:
        from_attributes = True


class StudentCareerPathBase(BaseModel):
    career_path_id: str


class StudentCareerPathCreate(StudentCareerPathBase):
    pass


class StudentCareerPathRead(BaseModel):
    id: str
    student_id: str
    career_path_id: str
    status: CareerPathStatus
    enrolled_at: datetime
    completion_pct: int = Field(ge=0, le=100)

    class Config:
        from_attributes = True


class CompanyBase(BaseModel):
    name: str = Field(max_length=255)
    logo_url: Optional[str] = Field(default=None, max_length=500)
    description: str = Field(default="")
    is_active: bool = Field(default=True)


class CompanyCreate(CompanyBase):
    pass


class CompanyRead(CompanyBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class SalaryRangeBase(BaseModel):
    career_path_id: str
    country: str = Field(max_length=100)
    min_salary: int = Field(ge=0)
    max_salary: int = Field(ge=0)
    avg_salary: int = Field(ge=0)
    currency: str = Field(default="USD", max_length=3)


class SalaryRangeCreate(SalaryRangeBase):
    pass


class SalaryRangeRead(SalaryRangeBase):
    id: str

    class Config:
        from_attributes = True


class JobOpeningBase(BaseModel):
    career_path_id: str
    company_id: str
    title: str = Field(max_length=255)
    location: str = Field(max_length=255)
    application_url: str = Field(max_length=500)
    description: str = Field(default="")
    is_active: bool = Field(default=True)


class JobOpeningCreate(JobOpeningBase):
    pass


class JobOpeningRead(JobOpeningBase):
    id: str
    posted_at: datetime
    company_name: Optional[str] = None

    class Config:
        from_attributes = True


class AlumniShowcaseBase(BaseModel):
    career_path_id: str
    student_id: Optional[str] = None
    name: str = Field(max_length=255)
    current_job_title: str = Field(max_length=255)
    company_name: str = Field(max_length=255)
    linkedin_url: Optional[str] = Field(default=None, max_length=500)
    story: str = Field(default="")
    is_featured: bool = Field(default=False)


class AlumniShowcaseCreate(AlumniShowcaseBase):
    pass


class AlumniShowcaseRead(AlumniShowcaseBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class CareerPathMarketDataBase(BaseModel):
    career_path_id: str
    job_market_summary: str = Field(default="")


class CareerPathMarketDataCreate(CareerPathMarketDataBase):
    pass


class CareerPathMarketDataRead(CareerPathMarketDataBase):
    id: str
    updated_at: datetime

    class Config:
        from_attributes = True


class CareerReadinessScore(BaseModel):
    career_path_id: str
    course_completion_score: float = Field(ge=0, le=100)
    quiz_performance_score: float = Field(ge=0, le=100)
    project_quality_score: float = Field(ge=0, le=100)
    portfolio_strength_score: float = Field(ge=0, le=100)
    mock_interview_score: float = Field(ge=0, le=100)
    total_score: float = Field(ge=0, le=100)
