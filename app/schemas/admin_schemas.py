"""
Pydantic schemas for Admin Control Panel operations.
Handles validation and serialization for all admin endpoints.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


# ──────────────────────────────────────────────────────────────
# COURSE SCHEMAS
# ──────────────────────────────────────────────────────────────

class CourseCreate(BaseModel):
    """Schema for creating a new course."""
    title: str = Field(..., max_length=200, description="Course title")
    description: str = Field(..., max_length=2000, description="Detailed course description")
    code: Optional[str] = Field(None, max_length=50, description="Course code (e.g., 'CSE101')")
    path_id: Optional[int] = Field(None, description="Optional career path ID")
    level_required: int = Field(default=1, ge=1, description="Minimum user level to access")
    level_unlocked: int = Field(default=1, ge=1, description="User level at which course unlocks")
    duration_weeks: int = Field(default=4, ge=1, description="Expected course duration in weeks")
    xp_reward: int = Field(default=100, ge=0, description="XP awarded on completion")
    difficulty: str = Field(default="intermediate", description="'beginner', 'intermediate', 'advanced', 'expert'")
    syllabus: Optional[str] = Field(None, max_length=5000, description="Course syllabus/outline")
    learning_outcomes: Optional[str] = Field(None, max_length=2000, description="JSON array of learning outcomes")
    has_quiz: bool = Field(default=True, description="Whether course includes quiz")
    quiz_passing_score: int = Field(default=70, ge=0, le=100, description="Required percentage to pass")
    has_certification: bool = Field(default=False, description="Whether course offers certification")

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v: str) -> str:
        allowed = {"beginner", "intermediate", "advanced", "expert"}
        if v not in allowed:
            raise ValueError(f"Difficulty must be one of {allowed}")
        return v


class CourseUpdate(BaseModel):
    """Schema for updating a course."""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    code: Optional[str] = Field(None, max_length=50)
    level_required: Optional[int] = Field(None, ge=1)
    level_unlocked: Optional[int] = Field(None, ge=1)
    duration_weeks: Optional[int] = Field(None, ge=1)
    xp_reward: Optional[int] = Field(None, ge=0)
    difficulty: Optional[str] = Field(None)
    syllabus: Optional[str] = Field(None, max_length=5000)
    learning_outcomes: Optional[str] = Field(None, max_length=2000)
    has_quiz: Optional[bool] = None
    quiz_passing_score: Optional[int] = Field(None, ge=0, le=100)
    has_certification: Optional[bool] = None
    status: Optional[str] = Field(None, description="'draft', 'published', 'archived'")
    is_active: Optional[bool] = None


class SyllabusUpdate(BaseModel):
    """Schema for updating course syllabus."""
    syllabus: str = Field(..., max_length=5000, description="Course syllabus content")
    learning_outcomes: Optional[str] = Field(None, max_length=2000, description="JSON array of outcomes")


class QuizConfig(BaseModel):
    """Schema for configuring course quiz."""
    has_quiz: bool = Field(default=True, description="Enable/disable quiz")
    passing_score: int = Field(default=70, ge=0, le=100, description="Passing score percentage")
    time_limit_minutes: Optional[int] = Field(None, ge=1, description="Quiz time limit in minutes")
    attempt_limit: Optional[int] = Field(None, ge=1, description="Max number of quiz attempts")
    shuffle_questions: bool = Field(default=True, description="Randomize question order")


class CourseRead(BaseModel):
    """Schema for reading course data."""
    course_id: int
    title: str
    description: str
    code: Optional[str]
    path_id: Optional[int]
    level_required: int
    level_unlocked: int
    duration_weeks: int
    xp_reward: int
    difficulty: str
    status: str
    is_active: bool
    has_quiz: bool
    quiz_passing_score: int
    has_certification: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────────────────────
# SKILL SCHEMAS
# ──────────────────────────────────────────────────────────────

class SkillCreate(BaseModel):
    """Schema for creating a new skill."""
    path_id: int = Field(..., description="Career path ID")
    name: str = Field(..., max_length=100, description="Skill name")
    category: str = Field(..., max_length=50, description="Skill category (e.g., 'backend', 'frontend')")
    level_required: int = Field(default=1, ge=1, description="Minimum user level to unlock")
    status: str = Field(default="locked", description="'locked', 'unlocked', 'in_progress', 'completed'")


class SkillUpdate(BaseModel):
    """Schema for updating a skill."""
    name: Optional[str] = Field(None, max_length=100)
    category: Optional[str] = Field(None, max_length=50)
    level_required: Optional[int] = Field(None, ge=1)
    status: Optional[str] = Field(None)


class SkillRead(BaseModel):
    """Schema for reading skill data."""
    skill_id: int
    path_id: int
    name: str
    category: str
    level_required: int
    status: str
    progress_pct: float

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────────────────────
# PROJECT SCHEMAS
# ──────────────────────────────────────────────────────────────

class ProjectCreate(BaseModel):
    """Schema for creating a new project."""
    path_id: int = Field(..., description="Career path ID")
    title: str = Field(..., max_length=150, description="Project title")
    description: str = Field(..., max_length=1000, description="Project description")
    level_required: int = Field(default=1, ge=1, description="Minimum user level to unlock")
    skills_needed: str = Field(..., max_length=500, description="Comma-separated required skills")
    xp_reward: int = Field(default=0, ge=0, description="XP awarded on completion")
    status: str = Field(default="locked", description="'locked', 'unlocked', 'in_progress', 'completed'")


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""
    title: Optional[str] = Field(None, max_length=150)
    description: Optional[str] = Field(None, max_length=1000)
    level_required: Optional[int] = Field(None, ge=1)
    skills_needed: Optional[str] = Field(None, max_length=500)
    xp_reward: Optional[int] = Field(None, ge=0)
    status: Optional[str] = Field(None)


class ProjectRead(BaseModel):
    """Schema for reading project data."""
    project_id: int
    path_id: int
    title: str
    description: str
    level_required: int
    skills_needed: str
    xp_reward: int
    status: str

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────────────────────
# RESOURCE SCHEMAS
# ──────────────────────────────────────────────────────────────

class ResourceCreate(BaseModel):
    """Schema for creating a resource."""
    path_id: int = Field(..., description="Career path ID")
    title: str = Field(..., max_length=200, description="Resource title")
    type: str = Field(..., max_length=50, description="'video', 'documentation', 'article', 'cheat_sheet'")
    url: Optional[str] = Field(None, max_length=500, description="Resource URL (for external resources)")
    level_range: str = Field(..., max_length=20, description="Level range (e.g., '1-10', '11-20')")
    is_locked: bool = Field(default=True, description="Whether resource is locked by default")


class ResourceUpdate(BaseModel):
    """Schema for updating a resource."""
    title: Optional[str] = Field(None, max_length=200)
    type: Optional[str] = Field(None, max_length=50)
    url: Optional[str] = Field(None, max_length=500)
    level_range: Optional[str] = Field(None, max_length=20)
    is_locked: Optional[bool] = None
    path_id: Optional[int] = None


class ResourceRead(BaseModel):
    """Schema for reading resource data."""
    resource_id: int
    path_id: int
    title: str
    type: str
    url: str
    level_range: str
    is_locked: bool

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────────────────────
# USER WARNING SCHEMAS
# ──────────────────────────────────────────────────────────────

class WarningCreate(BaseModel):
    """Schema for issuing a user warning."""
    severity: str = Field(..., description="'low', 'medium', 'high', 'critical'")
    reason: str = Field(..., max_length=500, description="Reason for warning")
    description: Optional[str] = Field(None, max_length=2000, description="Detailed description")

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v: str) -> str:
        allowed = {"low", "medium", "high", "critical"}
        if v not in allowed:
            raise ValueError(f"Severity must be one of {allowed}")
        return v


class WarningRead(BaseModel):
    """Schema for reading warning data."""
    warning_id: int
    user_id: int
    admin_id: int
    severity: str
    reason: str
    description: Optional[str]
    status: str
    is_active: bool
    issued_at: datetime

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────────────────────
# ANALYTICS SCHEMAS
# ──────────────────────────────────────────────────────────────

class PlatformHealthMetrics(BaseModel):
    """Platform health and engagement metrics."""
    total_users: int
    active_users: int
    banned_users: int
    total_courses: int
    user_retention_pct: float
    churn_rate: Optional[float] = None
    growth_rate: Optional[float] = None


class EngagementMetrics(BaseModel):
    """Platform engagement metrics."""
    days_period: int
    recently_active_users: int
    average_daily_streak: float
    engagement_rate: float
    total_sessions: Optional[int] = None


class CoursePerformanceMetrics(BaseModel):
    """Course performance statistics."""
    total_courses: int
    average_completion_rate: Optional[float] = None
    total_enrollments: Optional[int] = None
    course_stats: Optional[List[Dict[str, Any]]] = None


class AdminActivityMetrics(BaseModel):
    """Admin activity summary."""
    admin_id: int
    total_actions: int
    action_breakdown: Dict[str, int]
    failed_actions: int
    success_rate: float
    period_days: int


class AuditLogEntry(BaseModel):
    """Single audit log entry."""
    log_id: int
    admin_id: int
    action_type: str
    target_type: Optional[str]
    target_id: Optional[int]
    status: str
    timestamp: datetime
    details: Optional[str]
    ip_address: Optional[str]


# ──────────────────────────────────────────────────────────────
# PAGINATION & RESPONSE WRAPPERS
# ──────────────────────────────────────────────────────────────

class PaginatedResponse(BaseModel):
    """Generic paginated response wrapper."""
    items: List[Dict[str, Any]]
    total: int
    skip: int
    limit: int


class AdminStatsResponse(BaseModel):
    """Response for admin statistics."""
    total_actions: int
    success_count: int
    failed_count: int
    most_common_action: str
    last_action_time: Optional[datetime]
