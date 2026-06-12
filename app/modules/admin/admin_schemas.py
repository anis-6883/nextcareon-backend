"""app/modules/admin/schemas.py - Admin API schemas for CRUD operations."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.utils.validators import validate_password_strength


# ============================================================================
# User Management Schemas
# ============================================================================

class AdminUserCreate(BaseModel):
    """Create admin user."""
    full_name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    role: str = Field(default="content_manager", pattern="^(super_admin|content_manager|moderator)$")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return validate_password_strength(v)


class AdminUserUpdate(BaseModel):
    """Update admin user."""
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=255)
    role: Optional[str] = Field(default=None, pattern="^(super_admin|content_manager|moderator)$")


class AdminUserRead(BaseModel):
    """Read admin user."""
    id: str
    full_name: str
    email: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class StudentCreateAdmin(BaseModel):
    """Admin create student account."""
    full_name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    country: str = Field(default="Bangladesh", max_length=100)
    education_level: Optional[str] = None
    experience_level: Optional[str] = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return validate_password_strength(v)


class StudentUpdateAdmin(BaseModel):
    """Admin update student account."""
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=255)
    country: Optional[str] = Field(default=None, max_length=100)
    education_level: Optional[str] = None
    experience_level: Optional[str] = None
    dream_career: Optional[str] = Field(default=None, max_length=255)
    xp_points: Optional[int] = Field(default=None, ge=0)
    level: Optional[int] = Field(default=None, ge=1)
    coins: Optional[int] = Field(default=None, ge=0)


class StudentReadAdmin(BaseModel):
    """Admin view of student."""
    id: str
    full_name: str
    email: str
    country: str
    education_level: Optional[str]
    experience_level: Optional[str]
    dream_career: Optional[str]
    xp_points: int
    level: int
    coins: int
    daily_streak: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Course & Content Management Schemas
# ============================================================================

class LessonCreateAdmin(BaseModel):
    """Admin create lesson."""
    title: str = Field(min_length=1, max_length=255)
    content_text: str = Field(default="")
    content_image_url: Optional[str] = Field(default=None, max_length=500)
    code_snippets: Optional[Dict[str, str]] = Field(default=None)  # Multi-language code
    tts_audio_url: Optional[str] = Field(default=None, max_length=500)
    order_index: int = Field(ge=0)


class LessonUpdateAdmin(BaseModel):
    """Admin update lesson."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    content_text: Optional[str] = None
    content_image_url: Optional[str] = Field(default=None, max_length=500)
    code_snippets: Optional[Dict[str, str]] = None
    tts_audio_url: Optional[str] = Field(default=None, max_length=500)
    order_index: Optional[int] = Field(default=None, ge=0)


class LessonReadAdmin(BaseModel):
    """Admin read lesson."""
    id: str
    chapter_id: str
    course_id: str
    title: str
    content_text: str
    content_image_url: Optional[str]
    code_snippets: Optional[Dict[str, str]]
    tts_audio_url: Optional[str]
    order_index: int

    class Config:
        from_attributes = True


class ChapterCreateAdmin(BaseModel):
    """Admin create chapter."""
    title: str = Field(min_length=1, max_length=255)
    order_index: int = Field(ge=0)
    xp_reward: int = Field(default=0, ge=0)
    coin_reward: int = Field(default=0, ge=0)


class ChapterUpdateAdmin(BaseModel):
    """Admin update chapter."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    order_index: Optional[int] = Field(default=None, ge=0)
    xp_reward: Optional[int] = Field(default=None, ge=0)
    coin_reward: Optional[int] = Field(default=None, ge=0)


class ChapterReadAdmin(BaseModel):
    """Admin read chapter."""
    id: str
    course_id: str
    title: str
    order_index: int
    xp_reward: int
    coin_reward: int

    class Config:
        from_attributes = True


class CourseCreateAdmin(BaseModel):
    """Admin create course."""
    title: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=255)
    description: str = Field(default="")
    thumbnail_url: Optional[str] = Field(default=None, max_length=500)
    difficulty: str = Field(default="beginner", pattern="^(beginner|intermediate|advanced)$")
    estimated_hours: int = Field(default=0, ge=0)
    total_xp: int = Field(default=0, ge=0)


class CourseUpdateAdmin(BaseModel):
    """Admin update course."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    slug: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    thumbnail_url: Optional[str] = Field(default=None, max_length=500)
    difficulty: Optional[str] = Field(default=None, pattern="^(beginner|intermediate|advanced)$")
    estimated_hours: Optional[int] = Field(default=None, ge=0)
    total_xp: Optional[int] = Field(default=None, ge=0)


class CourseReadAdmin(BaseModel):
    """Admin read course."""
    id: str
    title: str
    slug: str
    description: str
    thumbnail_url: Optional[str]
    difficulty: str
    estimated_hours: int
    total_xp: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Quiz & Evaluation Schemas
# ============================================================================

class QuestionCreateAdmin(BaseModel):
    """Admin create quiz question."""
    question_text: str
    option_a: str = Field(max_length=500)
    option_b: str = Field(max_length=500)
    option_c: str = Field(max_length=500)
    option_d: str = Field(max_length=500)
    correct_option: str = Field(pattern="^[A-D]$")


class QuestionUpdateAdmin(BaseModel):
    """Admin update quiz question."""
    question_text: Optional[str] = None
    option_a: Optional[str] = Field(default=None, max_length=500)
    option_b: Optional[str] = Field(default=None, max_length=500)
    option_c: Optional[str] = Field(default=None, max_length=500)
    option_d: Optional[str] = Field(default=None, max_length=500)
    correct_option: Optional[str] = Field(default=None, pattern="^[A-D]$")


class QuestionReadAdmin(BaseModel):
    """Admin read quiz question."""
    id: str
    quiz_id: str
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: str

    class Config:
        from_attributes = True


class QuizCreateAdmin(BaseModel):
    """Admin create quiz."""
    pass_score: int = Field(default=60, ge=0, le=100)
    xp_reward: int = Field(default=100, ge=0)
    coin_reward: int = Field(default=25, ge=0)


class QuizUpdateAdmin(BaseModel):
    """Admin update quiz."""
    pass_score: Optional[int] = Field(default=None, ge=0, le=100)
    xp_reward: Optional[int] = Field(default=None, ge=0)
    coin_reward: Optional[int] = Field(default=None, ge=0)


class QuizReadAdmin(BaseModel):
    """Admin read quiz."""
    id: str
    chapter_id: str
    course_id: str
    pass_score: int
    xp_reward: int
    coin_reward: int

    class Config:
        from_attributes = True


# ============================================================================
# Assignment & Project Schemas
# ============================================================================

class AssignmentCreateAdmin(BaseModel):
    """Admin create assignment."""
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(default="")
    xp_reward: int = Field(default=50, ge=0)
    coin_reward: int = Field(default=100, ge=0)


class AssignmentUpdateAdmin(BaseModel):
    """Admin update assignment."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    xp_reward: Optional[int] = Field(default=None, ge=0)
    coin_reward: Optional[int] = Field(default=None, ge=0)


class AssignmentReadAdmin(BaseModel):
    """Admin read assignment."""
    id: str
    course_id: str
    title: str
    description: str
    xp_reward: int
    coin_reward: int

    class Config:
        from_attributes = True


class ProjectCreateAdmin(BaseModel):
    """Admin create project."""
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(default="")
    requirements_url: Optional[str] = Field(default=None, max_length=500)
    xp_reward: int = Field(default=100, ge=0)
    coin_reward: int = Field(default=300, ge=0)


class ProjectUpdateAdmin(BaseModel):
    """Admin update project."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    requirements_url: Optional[str] = Field(default=None, max_length=500)
    xp_reward: Optional[int] = Field(default=None, ge=0)
    coin_reward: Optional[int] = Field(default=None, ge=0)


class ProjectReadAdmin(BaseModel):
    """Admin read project."""
    id: str
    course_id: str
    title: str
    description: str
    requirements_url: Optional[str]
    xp_reward: int
    coin_reward: int

    class Config:
        from_attributes = True


# ============================================================================
# Audit Log Schemas
# ============================================================================

class AuditLogRead(BaseModel):
    """Read audit log entry."""
    id: str
    admin_id: str
    entity_type: str
    entity_id: str
    action_executed: str
    delta_payload_json: Dict[str, Any]
    reason_text: Optional[str]
    ip_address: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogFilter(BaseModel):
    """Filter audit logs."""
    entity_type: Optional[str] = None
    admin_id: Optional[str] = None
    action: Optional[str] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


# ============================================================================
# Gamification Schemas
# ============================================================================

class CoinEconomyConfig(BaseModel):
    """Configure coin economy parameters."""
    lesson_completion_coins: int = Field(default=10, ge=0)
    quiz_pass_coins: int = Field(default=25, ge=0)
    assignment_completion_coins: int = Field(default=100, ge=0)
    project_completion_coins: int = Field(default=300, ge=0)
    course_completion_coins: int = Field(default=500, ge=0)


class AchievementCreateAdmin(BaseModel):
    """Admin create achievement."""
    tier: str = Field(pattern="^(BRONZE|SILVER|GOLD|PLATINUM)$")
    metric_type: str = Field(pattern="^(QUIZZES_PASSED|PROJECTS_COMPLETED|COINS_EARNED)$")
    target_threshold: int = Field(ge=1)
    badge_image_url: Optional[str] = Field(default=None, max_length=500)


class AchievementUpdateAdmin(BaseModel):
    """Admin update achievement."""
    tier: Optional[str] = Field(default=None, pattern="^(BRONZE|SILVER|GOLD|PLATINUM)$")
    metric_type: Optional[str] = Field(default=None, pattern="^(QUIZZES_PASSED|PROJECTS_COMPLETED|COINS_EARNED)$")
    target_threshold: Optional[int] = Field(default=None, ge=1)
    badge_image_url: Optional[str] = Field(default=None, max_length=500)


class AchievementReadAdmin(BaseModel):
    """Admin read achievement."""
    id: str
    tier: str
    metric_type: str
    target_threshold: int
    badge_image_url: str

    class Config:
        from_attributes = True


class StoreItemCreateAdmin(BaseModel):
    """Admin create store item."""
    type: str = Field(pattern="^(PORTFOLIO_TEMPLATE|RESUME_TEMPLATE|PROJECT_TEMPLATE|DASHBOARD_THEME|AVATAR)$")
    name: str = Field(min_length=1, max_length=255)
    coin_cost: int = Field(ge=1)
    resource_payload_json: Optional[Dict[str, Any]] = Field(default=None)


class StoreItemUpdateAdmin(BaseModel):
    """Admin update store item."""
    type: Optional[str] = Field(default=None, pattern="^(PORTFOLIO_TEMPLATE|RESUME_TEMPLATE|PROJECT_TEMPLATE|DASHBOARD_THEME|AVATAR)$")
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    coin_cost: Optional[int] = Field(default=None, ge=1)
    resource_payload_json: Optional[Dict[str, Any]] = None


class StoreItemReadAdmin(BaseModel):
    """Admin read store item."""
    id: str
    type: str
    name: str
    coin_cost: int
    resource_payload_json: Dict[str, Any]

    class Config:
        from_attributes = True


# ============================================================================
# Career Path & Market Intelligence Schemas
# ============================================================================

class CareerPathCreateAdmin(BaseModel):
    """Admin create career path."""
    title: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=255)
    description: str = Field(default="")
    course_ids: List[str] = Field(default_factory=list)


class CareerPathUpdateAdmin(BaseModel):
    """Admin update career path."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    slug: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    course_ids: Optional[List[str]] = None


class CareerPathReadAdmin(BaseModel):
    """Admin read career path."""
    id: str
    title: str
    slug: str
    description: str

    class Config:
        from_attributes = True


class CompanyCreateAdmin(BaseModel):
    """Admin create company."""
    name: str = Field(min_length=1, max_length=255)
    logo_url: Optional[str] = Field(default=None, max_length=500)


class CompanyUpdateAdmin(BaseModel):
    """Admin update company."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    logo_url: Optional[str] = Field(default=None, max_length=500)


class CompanyReadAdmin(BaseModel):
    """Admin read company."""
    id: str
    name: str
    logo_url: Optional[str]

    class Config:
        from_attributes = True


class SalaryRangeCreateAdmin(BaseModel):
    """Admin create salary range."""
    career_path_id: str
    entry_level_min: int = Field(ge=0)
    entry_level_max: int = Field(ge=0)
    senior_level_min: int = Field(ge=0)
    senior_level_max: int = Field(ge=0)
    currency: str = Field(default="USD", max_length=10)


class SalaryRangeUpdateAdmin(BaseModel):
    """Admin update salary range."""
    entry_level_min: Optional[int] = Field(default=None, ge=0)
    entry_level_max: Optional[int] = Field(default=None, ge=0)
    senior_level_min: Optional[int] = Field(default=None, ge=0)
    senior_level_max: Optional[int] = Field(default=None, ge=0)
    currency: Optional[str] = Field(default=None, max_length=10)


# ============================================================================
# Score Override Schemas
# ============================================================================

class CareerScoreOverride(BaseModel):
    """Override a student's career score component."""
    metric_type: str = Field(
        pattern="^(COURSE_COMPLETION|QUIZ|PROJECT|PORTFOLIO|INTERVIEW|TOTAL)$"
    )
    new_value: float = Field(ge=0, le=100)
    reason: str = Field(min_length=10, max_length=1000)


class CareerScoreRead(BaseModel):
    """Read career score."""
    id: str
    student_id: str
    course_completion_score: float
    quiz_performance_score: float
    project_quality_score: float
    portfolio_strength_score: float
    mock_interview_score: float
    total_career_score: float
    last_calculated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ============================================================================
# AI Assistant Configuration Schemas
# ============================================================================

class AiGateConfigUpdate(BaseModel):
    """Update AI gate configuration."""
    coins_per_ai_question: int = Field(default=10, ge=1)
    questions_per_exchange: int = Field(default=10, ge=1)
    max_tokens_per_response: int = Field(default=1024, ge=100)
