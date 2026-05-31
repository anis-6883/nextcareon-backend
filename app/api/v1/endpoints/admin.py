from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Query, Request
from sqlmodel import Session, select, func
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pathlib import Path
import json
import os

from app.db.session import get_session
from app.schemas.auth_schemas import AdminLogin, AdminRegister, AdminRead, TokenResponse
from app.schemas.admin_schemas import (
    CourseCreate, CourseUpdate, CourseRead, SyllabusUpdate, QuizConfig,
    SkillCreate, SkillUpdate, SkillRead,
    ProjectCreate, ProjectUpdate, ProjectRead,
    ResourceCreate, ResourceUpdate, ResourceRead,
    WarningCreate, WarningRead,
    PlatformHealthMetrics, EngagementMetrics, CoursePerformanceMetrics
)
from app.schemas.response import StandardResponse
from app.models.admin import Admin
from app.models.user import User
from app.models.course import Course
from app.models.skill import Skill
from app.models.project import Project
from app.models.resource import Resource
from app.models.audit_log import AdminAuditLog
from app.models.user_warning import UserWarning
from app.core import security
from app.core.config import settings
from app.core.dependencies import get_current_admin, get_request_context, RequestContext
from app.services import auth_service
from app.services.audit_service import AuditService

router = APIRouter(prefix="/admin", tags=["admin"])



# AUTHENTICATION ENDPOINTS


@router.post("/auth/register", response_model=StandardResponse[AdminRead], status_code=status.HTTP_201_CREATED)
def admin_register(payload: AdminRegister, db: Session = Depends(get_session)):
    """Register a new admin user (protected endpoint - admin only)"""
    existing = db.exec(select(Admin).where(Admin.username == payload.username)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed = security.get_password_hash(payload.password)
    admin = Admin(
        username=payload.username,
        password=hashed,
        permissions=payload.permissions,
        is_active=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return StandardResponse(
        status=True,
        message="Admin registered successfully!",
        data=AdminRead.from_orm(admin)
    )

@router.post("/auth/login", response_model=StandardResponse[TokenResponse])
def admin_login(payload: AdminLogin, db: Session = Depends(get_session)):
    """Admin login endpoint - returns JWT token"""
    admin = auth_service.authenticate_admin(db, payload.username, payload.password)
    if not admin:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")

    tokens = auth_service.create_tokens_for_admin(admin)
    admin.last_login = datetime.utcnow()
    db.add(admin)
    db.commit()

    AuditService.log_action(
        db, admin.admin_id, "ADMIN_LOGIN", 
        status="success"
    )

    return StandardResponse(
        status=True,
        message="Admin logged in successfully!",
        data=TokenResponse(**tokens)
    )

@router.post("/auth/logout")
def admin_logout(admin: Admin = Depends(get_current_admin), db: Session = Depends(get_session)):
    """Admin logout - logs the session termination"""
    AuditService.log_action(
        db, admin.admin_id, "ADMIN_LOGOUT",
        status="success"
    )
    return StandardResponse(
        status=True,
        message="Admin logged out successfully!"
    )

@router.get("/auth/me", response_model=StandardResponse[AdminRead])
def admin_me(admin: Admin = Depends(get_current_admin)):
    """Get current admin profile"""
    return StandardResponse(
        status=True,
        message="Admin profile fetched successfully!",
        data=AdminRead.from_orm(admin)
    )



# CONTENT MANAGEMENT - COURSES


@router.post("/courses", response_model=StandardResponse[CourseRead], status_code=status.HTTP_201_CREATED)
def create_course(
    payload: CourseCreate,
    request: Request,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_session),
):
    """Create a new course"""
    try:
        course = Course(**payload.dict(exclude_unset=True))
        db.add(course)
        db.commit()
        db.refresh(course)

        AuditService.log_action(
            db, admin.admin_id, "COURSE_CREATED",
            target_type="COURSE", target_id=course.course_id,
            details={"course_title": course.title, "code": course.code},
            ip_address=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", "")
        )

        return StandardResponse(
            status=True,
            message="Course created successfully",
            data=CourseRead.from_orm(course)
        )
    except Exception as e:
        AuditService.log_action(
            db, admin.admin_id, "COURSE_CREATED",
            status="failed", error_message=str(e),
            ip_address=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", "")
        )
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/courses", response_model=StandardResponse[Dict[str, Any]])
def list_courses(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """List all courses with pagination"""
    courses = db.exec(select(Course).offset(skip).limit(limit)).all()
    total = db.exec(select(func.count(Course.course_id))).one()
    return StandardResponse(
        status=True,
        message="Courses retrieved successfully",
        data={
            "courses": [CourseRead.from_orm(c).dict() for c in courses],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    )

@router.get("/courses/{course_id}", response_model=StandardResponse[CourseRead])
def get_course(
    course_id: int,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Get specific course details"""
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return StandardResponse(
        status=True,
        message="Course retrieved successfully",
        data=CourseRead.from_orm(course)
    )

@router.put("/courses/{course_id}", response_model=StandardResponse[CourseRead])
def update_course(
    course_id: int,
    payload: CourseUpdate,
    request: Request,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_session),
):
    """Update course details"""
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    update_data = payload.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(course, key, value)
    course.updated_at = datetime.utcnow()
    db.add(course)
    db.commit()
    db.refresh(course)

    AuditService.log_action(
        db, admin.admin_id, "COURSE_UPDATED",
        target_type="COURSE", target_id=course_id,
        details={"changes": update_data},
        ip_address=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent", "")
    )

    return StandardResponse(
        status=True,
        message="Course updated successfully",
        data=CourseRead.from_orm(course)
    )

@router.delete("/courses/{course_id}", response_model=StandardResponse)
def delete_course(
    course_id: int,
    request: Request,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_session),
):
    """Delete a course"""
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    course_title = course.title
    db.delete(course)
    db.commit()

    AuditService.log_action(
        db, admin.admin_id, "COURSE_DELETED",
        target_type="COURSE", target_id=course_id,
        details={"course_title": course_title},
        ip_address=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent", "")
    )

    return StandardResponse(status=True, message="Course deleted successfully")

@router.post("/courses/{course_id}/syllabus", response_model=StandardResponse[CourseRead])
def update_course_syllabus(
    course_id: int,
    payload: SyllabusUpdate,
    request: Request,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_session),
):
    """Update course syllabus and learning outcomes"""
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    course.syllabus = payload.syllabus
    if payload.learning_outcomes:
        course.learning_outcomes = payload.learning_outcomes
    course.updated_at = datetime.utcnow()
    db.add(course)
    db.commit()
    db.refresh(course)

    AuditService.log_action(
        db, admin.admin_id, "COURSE_SYLLABUS_UPDATED",
        target_type="COURSE", target_id=course_id,
        details={"has_learning_outcomes": payload.learning_outcomes is not None},
        ip_address=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent", "")
    )

    return StandardResponse(
        status=True,
        message="Course syllabus updated successfully",
        data=CourseRead.from_orm(course)
    )

@router.put("/courses/{course_id}/quiz-config", response_model=StandardResponse[CourseRead])
def configure_course_quiz(
    course_id: int,
    payload: QuizConfig,
    request: Request,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_session),
):
    """Configure course quiz settings"""
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    course.has_quiz = payload.has_quiz
    course.quiz_passing_score = payload.passing_score
    course.updated_at = datetime.utcnow()
    db.add(course)
    db.commit()
    db.refresh(course)

    AuditService.log_action(
        db, admin.admin_id, "COURSE_QUIZ_CONFIGURED",
        target_type="COURSE", target_id=course_id,
        details={"has_quiz": payload.has_quiz, "passing_score": payload.passing_score},
        ip_address=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent", "")
    )

    return StandardResponse(
        status=True,
        message="Course quiz configured successfully",
        data=CourseRead.from_orm(course)
    )



# CONTENT MANAGEMENT - SKILLS


@router.post("/skills", response_model=StandardResponse[SkillRead], status_code=status.HTTP_201_CREATED)
def create_skill(
    payload: SkillCreate,
    request: Request,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_session),
):
    """Create a new skill"""
    try:
        skill = Skill(**payload.dict())
        db.add(skill)
        db.commit()
        db.refresh(skill)

        AuditService.log_action(
            db, admin.admin_id, "SKILL_CREATED",
            target_type="SKILL", target_id=skill.skill_id,
            details={"skill_name": skill.name, "category": skill.category},
            ip_address=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", "")
        )

        return StandardResponse(
            status=True,
            message="Skill created successfully",
            data=SkillRead.from_orm(skill)
        )
    except Exception as e:
        AuditService.log_action(
            db, admin.admin_id, "SKILL_CREATED",
            status="failed", error_message=str(e),
            ip_address=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", "")
        )
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/skills", response_model=StandardResponse[Dict[str, Any]])
def list_skills(
    path_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """List all skills with optional filtering"""
    query = select(Skill)
    if path_id:
        query = query.where(Skill.path_id == path_id)
    
    skills = db.exec(query.offset(skip).limit(limit)).all()
    total = db.exec(select(func.count(Skill.skill_id))).one()
    
    return StandardResponse(
        status=True,
        message="Skills retrieved successfully",
        data={
            "skills": [SkillRead.from_orm(s).dict() for s in skills],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    )

@router.get("/skills/{skill_id}", response_model=StandardResponse[SkillRead])
def get_skill(
    skill_id: int,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Get specific skill details"""
    skill = db.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return StandardResponse(
        status=True,
        message="Skill retrieved successfully",
        data=SkillRead.from_orm(skill)
    )

@router.put("/skills/{skill_id}", response_model=StandardResponse[SkillRead])
def update_skill(
    skill_id: int,
    payload: SkillUpdate,
    request: Request,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_session),
):
    """Update skill details"""
    skill = db.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    update_data = payload.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(skill, key, value)
    db.add(skill)
    db.commit()
    db.refresh(skill)

    AuditService.log_action(
        db, admin.admin_id, "SKILL_UPDATED",
        target_type="SKILL", target_id=skill_id,
        details={"changes": update_data},
        ip_address=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent", "")
    )

    return StandardResponse(
        status=True,
        message="Skill updated successfully",
        data=SkillRead.from_orm(skill)
    )

@router.delete("/skills/{skill_id}", response_model=StandardResponse)
def delete_skill(
    skill_id: int,
    request: Request,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_session),
):
    """Delete a skill"""
    skill = db.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    skill_name = skill.name
    db.delete(skill)
    db.commit()

    AuditService.log_action(
        db, admin.admin_id, "SKILL_DELETED",
        target_type="SKILL", target_id=skill_id,
        details={"skill_name": skill_name},
        ip_address=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent", "")
    )

    return StandardResponse(status=True, message="Skill deleted successfully")



# CONTENT MANAGEMENT - PROJECTS


@router.post("/projects", response_model=StandardResponse[ProjectRead], status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    request: Request,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_session),
):
    """Create a new project"""
    try:
        project = Project(**payload.dict())
        db.add(project)
        db.commit()
        db.refresh(project)

        AuditService.log_action(
            db, admin.admin_id, "PROJECT_CREATED",
            target_type="PROJECT", target_id=project.project_id,
            details={"project_title": project.title},
            ip_address=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", "")
        )

        return StandardResponse(
            status=True,
            message="Project created successfully",
            data=ProjectRead.from_orm(project)
        )
    except Exception as e:
        AuditService.log_action(
            db, admin.admin_id, "PROJECT_CREATED",
            status="failed", error_message=str(e),
            ip_address=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", "")
        )
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/projects", response_model=StandardResponse[Dict[str, Any]])
def list_projects(
    path_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """List all projects with optional filtering"""
    query = select(Project)
    if path_id:
        query = query.where(Project.path_id == path_id)
    
    projects = db.exec(query.offset(skip).limit(limit)).all()
    total = db.exec(select(func.count(Project.project_id))).one()
    
    return StandardResponse(
        status=True,
        message="Projects retrieved successfully",
        data={
            "projects": [ProjectRead.from_orm(p).dict() for p in projects],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    )

@router.get("/projects/{project_id}", response_model=StandardResponse[ProjectRead])
def get_project(
    project_id: int,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Get specific project details"""
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return StandardResponse(
        status=True,
        message="Project retrieved successfully",
        data=ProjectRead.from_orm(project)
    )

@router.put("/projects/{project_id}", response_model=StandardResponse[ProjectRead])
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    request: Request,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_session),
):
    """Update project details"""
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    update_data = payload.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)
    db.add(project)
    db.commit()
    db.refresh(project)

    AuditService.log_action(
        db, admin.admin_id, "PROJECT_UPDATED",
        target_type="PROJECT", target_id=project_id,
        details={"changes": update_data},
        ip_address=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent", "")
    )

    return StandardResponse(
        status=True,
        message="Project updated successfully",
        data=ProjectRead.from_orm(project)
    )

@router.delete("/projects/{project_id}", response_model=StandardResponse)
def delete_project(
    project_id: int,
    request: Request,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_session),
):
    """Delete a project"""
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project_title = project.title
    db.delete(project)
    db.commit()

    AuditService.log_action(
        db, admin.admin_id, "PROJECT_DELETED",
        target_type="PROJECT", target_id=project_id,
        details={"project_title": project_title},
        ip_address=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent", "")
    )

    return StandardResponse(status=True, message="Project deleted successfully")



# USER MANAGEMENT ENDPOINTS


@router.get("/users", response_model=StandardResponse[Dict[str, Any]])
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """List all users with pagination"""
    users = db.exec(select(User).offset(skip).limit(limit)).all()
    total = db.exec(select(func.count(User.user_id))).one()
    return StandardResponse(
        status=True,
        message="Users retrieved successfully",
        data={
            "users": [
                {
                    "user_id": u.user_id,
                    "name": u.name,
                    "email": u.email,
                    "level": u.level,
                    "xp_point": u.xp_point,
                    "is_active": u.is_active,
                    "role": u.role,
                    "created_at": u.created_at
                }
                for u in users
            ],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    )

@router.get("/users/{user_id}", response_model=StandardResponse[Dict[str, Any]])
def get_user_details(
    user_id: int,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Get detailed user information with statistics"""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    warnings_count = db.exec(
        select(func.count(UserWarning.warning_id)).where(UserWarning.user_id == user_id)
    ).one()
    
    active_warnings = db.exec(
        select(func.count(UserWarning.warning_id)).where(
            (UserWarning.user_id == user_id) & (UserWarning.is_active == True)
        )
    ).one()

    return StandardResponse(
        status=True,
        message="User details retrieved successfully",
        data={
            "user": {
                "user_id": user.user_id,
                "name": user.name,
                "email": user.email,
                "level": user.level,
                "xp_point": user.xp_point,
                "dept": user.dept,
                "dailystreak": user.dailystreak,
                "is_active": user.is_active,
                "role": user.role,
                "last_login": user.last_login,
                "created_at": user.created_at
            },
            "statistics": {
                "account_age_days": (datetime.utcnow() - user.created_at).days,
                "total_warnings": warnings_count,
                "active_warnings": active_warnings,
                "status": "active" if user.is_active else "inactive"
            }
        }
    )

@router.post("/users/{user_id}/warn", response_model=StandardResponse[WarningRead], status_code=status.HTTP_201_CREATED)
def issue_warning(
    user_id: int,
    payload: WarningCreate,
    request: Request,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_session),
):
    """Issue a formal warning to a user"""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    warning = UserWarning(
        user_id=user_id,
        admin_id=admin.admin_id,
        severity=payload.severity,
        reason=payload.reason,
        description=payload.description,
        is_active=True
    )
    db.add(warning)
    db.commit()
    db.refresh(warning)

    AuditService.log_action(
        db, admin.admin_id, "USER_WARNED",
        target_type="USER", target_id=user_id,
        details={"reason": warning.reason, "severity": warning.severity},
        ip_address=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent", "")
    )

    return StandardResponse(
        status=True,
        message="Warning issued successfully",
        data=WarningRead.from_orm(warning)
    )

@router.post("/users/{user_id}/suspend", response_model=StandardResponse)
def suspend_user(
    user_id: int,
    request: Request,
    reason: Optional[str] = Query(None, max_length=500),
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_session),
):
    """Suspend user account"""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    db.add(user)
    db.commit()

    AuditService.log_action(
        db, admin.admin_id, "USER_SUSPENDED",
        target_type="USER", target_id=user_id,
        details={"reason": reason},
        ip_address=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent", "")
    )

    return StandardResponse(status=True, message="User suspended successfully")

@router.post("/users/{user_id}/unsuspend", response_model=StandardResponse)
def unsuspend_user(
    user_id: int,
    request: Request,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_session),
):
    """Unsuspend user account"""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = True
    db.add(user)
    db.commit()

    AuditService.log_action(
        db, admin.admin_id, "USER_UNSUSPENDED",
        target_type="USER", target_id=user_id,
        ip_address=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent", "")
    )

    return StandardResponse(status=True, message="User unsuspended successfully")

@router.post("/users/{user_id}/ban", response_model=StandardResponse)
def ban_user(
    user_id: int,
    request: Request,
    reason: Optional[str] = Query(None, max_length=500),
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_session),
):
    """Permanently ban user account"""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    user.role = "banned"
    db.add(user)
    db.commit()

    AuditService.log_action(
        db, admin.admin_id, "USER_BANNED",
        target_type="USER", target_id=user_id,
        details={"reason": reason},
        ip_address=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent", "")
    )

    return StandardResponse(status=True, message="User banned permanently")



# RESOURCE MANAGEMENT ENDPOINTS


@router.post("/resources/upload", response_model=StandardResponse[ResourceRead], status_code=status.HTTP_201_CREATED)
async def upload_resource(
    file: UploadFile = File(...),
    path_id: int = Query(..., gt=0),
    title: str = Query(..., max_length=200),
    resource_type: str = Query(..., max_length=50),
    level_range: str = Query(..., max_length=20),
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_session),
    request: Request = None,
):
    """Upload a new learning resource (video, document, etc.)"""
    file_ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if file_ext not in settings.ADMIN_ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed: {', '.join(settings.ADMIN_ALLOWED_FILE_TYPES)}"
        )

    file_path = None
    try:
        upload_dir = Path("uploads/resources") / str(path_id)
        upload_dir.mkdir(parents=True, exist_ok=True)

        contents = await file.read()
        file_size_mb = len(contents) / (1024 * 1024)

        if file_size_mb > settings.ADMIN_MAX_FILE_SIZE_MB:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {settings.ADMIN_MAX_FILE_SIZE_MB}MB"
            )

        file_location = upload_dir / file.filename
        with open(file_location, "wb") as f:
            f.write(contents)
        file_path = str(file_location)

        resource = Resource(
            path_id=path_id,
            title=title,
            type=resource_type,
            url=file_path,
            level_range=level_range,
            is_locked=False
        )
        db.add(resource)
        db.commit()
        db.refresh(resource)

        AuditService.log_action(
            db, admin.admin_id, "RESOURCE_UPLOADED",
            target_type="RESOURCE", target_id=resource.resource_id,
            details={"filename": file.filename, "size_mb": round(file_size_mb, 2), "type": resource_type},
            ip_address=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", "")
        )

        return StandardResponse(
            status=True,
            message="Resource uploaded successfully",
            data=ResourceRead.from_orm(resource)
        )

    except Exception as e:
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass

        AuditService.log_action(
            db, admin.admin_id, "RESOURCE_UPLOADED",
            status="failed", error_message=str(e),
            ip_address=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", "")
        )
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/resources", response_model=StandardResponse[Dict[str, Any]])
def list_resources(
    path_id: Optional[int] = None,
    resource_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """List resources with optional filtering"""
    query = select(Resource)
    if path_id:
        query = query.where(Resource.path_id == path_id)
    if resource_type:
        query = query.where(Resource.type == resource_type)
    
    resources = db.exec(query.offset(skip).limit(limit)).all()
    total = db.exec(select(func.count(Resource.resource_id))).one()
    
    return StandardResponse(
        status=True,
        message="Resources retrieved successfully",
        data={
            "resources": [ResourceRead.from_orm(r).dict() for r in resources],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    )

@router.put("/resources/{resource_id}", response_model=StandardResponse[ResourceRead])
def update_resource(
    resource_id: int,
    payload: ResourceUpdate,
    request: Request,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_session),
):
    """Update resource metadata"""
    resource = db.get(Resource, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    update_data = payload.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(resource, key, value)
    db.add(resource)
    db.commit()
    db.refresh(resource)

    AuditService.log_action(
        db, admin.admin_id, "RESOURCE_UPDATED",
        target_type="RESOURCE", target_id=resource_id,
        details={"changes": update_data},
        ip_address=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent", "")
    )

    return StandardResponse(
        status=True,
        message="Resource updated successfully",
        data=ResourceRead.from_orm(resource)
    )

@router.delete("/resources/{resource_id}", response_model=StandardResponse)
def delete_resource(
    resource_id: int,
    request: Request,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_session),
):
    """Delete a resource"""
    resource = db.get(Resource, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    if resource.url and os.path.exists(resource.url):
        try:
            os.remove(resource.url)
        except:
            pass

    db.delete(resource)
    db.commit()

    AuditService.log_action(
        db, admin.admin_id, "RESOURCE_DELETED",
        target_type="RESOURCE", target_id=resource_id,
        details={"url": resource.url},
        ip_address=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent", "")
    )

    return StandardResponse(status=True, message="Resource deleted successfully")

# SYSTEM ANALYTICS & HEALTH ENDPOINTS (Read-Only)


@router.get("/analytics/platform-health", response_model=StandardResponse[PlatformHealthMetrics])
def get_platform_health(
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Get overall platform health metrics"""
    total_users = db.exec(select(func.count(User.user_id))).one()
    active_users = db.exec(
        select(func.count(User.user_id)).where(User.is_active == True)
    ).one()
    banned_users = db.exec(
        select(func.count(User.user_id)).where(User.role == "banned")
    ).one()
    total_courses = db.exec(select(func.count(Course.course_id))).one()

    retention_pct = (active_users / total_users * 100) if total_users > 0 else 0

    return StandardResponse(
        status=True,
        message="Platform health metrics retrieved successfully",
        data=PlatformHealthMetrics(
            total_users=total_users,
            active_users=active_users,
            banned_users=banned_users,
            total_courses=total_courses,
            user_retention_pct=retention_pct
        )
    )

@router.get("/analytics/engagement", response_model=StandardResponse[EngagementMetrics])
def get_engagement_metrics(
    days: int = Query(30, ge=1, le=365),
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Get platform engagement metrics for last N days"""
    start_date = datetime.utcnow() - timedelta(days=days)

    active_recent = db.exec(
        select(func.count(User.user_id)).where(User.last_login >= start_date)
    ).one()

    avg_streak = db.exec(select(func.avg(User.dailystreak))).one() or 0
    
    total_users = db.exec(select(func.count(User.user_id))).one()
    engagement_rate = (active_recent / total_users * 100) if total_users > 0 else 0

    return StandardResponse(
        status=True,
        message="Engagement metrics retrieved successfully",
        data=EngagementMetrics(
            days_period=days,
            recently_active_users=active_recent,
            average_daily_streak=round(avg_streak, 2),
            engagement_rate=round(engagement_rate, 2)
        )
    )

@router.get("/analytics/course-performance", response_model=StandardResponse[CoursePerformanceMetrics])
def get_course_performance(
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Get course completion and performance statistics"""
    total_courses = db.exec(select(func.count(Course.course_id))).one()

    return StandardResponse(
        status=True,
        message="Course performance metrics retrieved successfully",
        data=CoursePerformanceMetrics(
            total_courses=total_courses,
            average_completion_rate=None,
            total_enrollments=None
        )
    )

@router.get("/audit-logs", response_model=StandardResponse[Dict[str, Any]])
def get_audit_logs(
    admin_id: Optional[int] = None,
    action_type: Optional[str] = None,
    days: int = Query(7, ge=1, le=365),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Get audit logs with optional filtering"""
    start_date = datetime.utcnow() - timedelta(days=days)

    logs = AuditService.get_logs(
        db,
        admin_id=admin_id,
        action_type=action_type,
        start_date=start_date,
        limit=limit,
        offset=skip
    )

    total = AuditService.get_log_count(
        db,
        admin_id=admin_id,
        action_type=action_type,
        start_date=start_date
    )

    return StandardResponse(
        status=True,
        message="Audit logs retrieved successfully",
        data={
            "logs": [
                {
                    "log_id": l.log_id,
                    "admin_id": l.admin_id,
                    "action_type": l.action_type,
                    "target_type": l.target_type,
                    "target_id": l.target_id,
                    "status": l.status,
                    "timestamp": l.timestamp.isoformat() if l.timestamp else None,
                    "details": l.details,
                    "ip_address": l.ip_address
                }
                for l in logs
            ],
            "total": total,
            "days_period": days,
            "skip": skip,
            "limit": limit
        }
    )

@router.get("/admin-activity", response_model=StandardResponse[Dict[str, Any]])
def get_admin_activity(
    admin_id: int = Query(..., gt=0),
    days: int = Query(7, ge=1, le=365),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    """Get activity summary for a specific admin"""
    activity = AuditService.get_admin_activity(db, admin_id, days)

    return StandardResponse(
        status=True,
        message="Admin activity retrieved successfully",
        data=activity
    )

