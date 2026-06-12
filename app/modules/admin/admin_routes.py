"""app/modules/admin/admin_routes.py - Comprehensive admin CRUD routes."""

from typing import List
from typing import Optional
from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.engine import get_session
from app.core.dependencies import get_current_admin
from app.modules.users.models import AdminUser, Student
from app.modules.courses.models import Course, Chapter, Lesson, Quiz, Question, Assignment, Project

from app.modules.admin.admin_schemas import (
    AdminUserRead, AdminUserCreate, AdminUserUpdate,
    StudentReadAdmin, StudentCreateAdmin, StudentUpdateAdmin,
    CourseReadAdmin, CourseCreateAdmin, CourseUpdateAdmin,
    ChapterReadAdmin, ChapterCreateAdmin, ChapterUpdateAdmin,
    LessonReadAdmin, LessonCreateAdmin, LessonUpdateAdmin,
    QuizReadAdmin, QuizCreateAdmin, QuizUpdateAdmin,
    QuestionReadAdmin, QuestionCreateAdmin, QuestionUpdateAdmin,
    AssignmentReadAdmin, AssignmentCreateAdmin, AssignmentUpdateAdmin,
    ProjectReadAdmin, ProjectCreateAdmin, ProjectUpdateAdmin,
    AuditLogRead, AuditLogFilter,
)
from app.modules.admin.admin_service import (
    create_admin_user, update_admin_user, delete_admin_user, get_all_admin_users,
    create_student_admin, update_student_admin, delete_student_admin,
    create_course_admin, update_course_admin, delete_course_admin,
    create_chapter_admin, update_chapter_admin, delete_chapter_admin,
    create_lesson_admin, update_lesson_admin, delete_lesson_admin,
    create_quiz_admin, update_quiz_admin,
    create_question_admin, update_question_admin, delete_question_admin,
    create_assignment_admin, update_assignment_admin, delete_assignment_admin,
    create_project_admin, update_project_admin, delete_project_admin,
)
from app.modules.admin.audit_service import get_audit_logs
from app.modules.admin.audit_models import AuditActionType


router = APIRouter(prefix="/admin", tags=["admin"])


# ============================================================================
# Admin User Management
# ============================================================================

@router.post("/users", response_model=AdminUserRead, status_code=status.HTTP_201_CREATED)
async def create_admin_endpoint(
    data: AdminUserCreate,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Create a new admin user (admin only)."""
    new_admin = await create_admin_user(
        session,
        admin_id=admin.id,
        full_name=data.full_name,
        email=data.email,
        password=data.password,
        role=data.role,
    )
    return AdminUserRead.model_validate(new_admin)


@router.get("/users", response_model=List[AdminUserRead])
async def list_admins_endpoint(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """List all admin users."""
    admins = await get_all_admin_users(session, limit=limit, offset=skip)
    return [AdminUserRead.model_validate(a) for a in admins]


@router.get("/users/{admin_id}", response_model=AdminUserRead)
async def get_admin_endpoint(
    admin_id: str,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Get a specific admin user."""
    target = await session.get(AdminUser, admin_id)
    if not target:
        raise HTTPException(status_code=404, detail="Admin user not found")
    return AdminUserRead.model_validate(target)


@router.patch("/users/{admin_id}", response_model=AdminUserRead)
async def update_admin_endpoint(
    admin_id: str,
    data: AdminUserUpdate,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Update an admin user."""
    updated = await update_admin_user(
        session,
        admin_id=admin.id,
        target_admin_id=admin_id,
        update_data=data.model_dump(exclude_unset=True),
    )
    return AdminUserRead.model_validate(updated)


@router.delete("/users/{admin_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_admin_endpoint(
    admin_id: str,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Delete an admin user."""
    await delete_admin_user(session, admin_id=admin.id, target_admin_id=admin_id)


# ============================================================================
# Student Management
# ============================================================================

@router.post("/students", response_model=StudentReadAdmin, status_code=status.HTTP_201_CREATED)
async def create_student_endpoint(
    data: StudentCreateAdmin,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Create a new student (admin only)."""
    student = await create_student_admin(
        session,
        admin_id=admin.id,
        full_name=data.full_name,
        email=data.email,
        password=data.password,
        country=data.country,
        education_level=data.education_level,
        experience_level=data.experience_level,
    )
    return StudentReadAdmin.model_validate(student)


@router.get("/students", response_model=List[StudentReadAdmin])
async def list_students_endpoint(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """List all students."""
    result = await session.execute(
        select(Student).offset(skip).limit(limit)
    )
    students = result.scalars().all()
    return [StudentReadAdmin.model_validate(s) for s in students]


@router.get("/students/{student_id}", response_model=StudentReadAdmin)
async def get_student_endpoint(
    student_id: str,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Get a specific student."""
    student = await session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return StudentReadAdmin.model_validate(student)


@router.patch("/students/{student_id}", response_model=StudentReadAdmin)
async def update_student_endpoint(
    student_id: str,
    data: StudentUpdateAdmin,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Update a student."""
    student = await update_student_admin(
        session,
        admin_id=admin.id,
        student_id=student_id,
        update_data=data.model_dump(exclude_unset=True),
    )
    return StudentReadAdmin.model_validate(student)


@router.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student_endpoint(
    student_id: str,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Delete a student."""
    await delete_student_admin(session, admin_id=admin.id, student_id=student_id)


# ============================================================================
# Course Management
# ============================================================================

@router.post("/courses", response_model=CourseReadAdmin, status_code=status.HTTP_201_CREATED)
async def create_course_endpoint(
    data: CourseCreateAdmin,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Create a new course."""
    course = await create_course_admin(
        session,
        admin_id=admin.id,
        **data.model_dump(),
    )
    return CourseReadAdmin.model_validate(course)


@router.get("/courses", response_model=List[CourseReadAdmin])
async def list_courses_endpoint(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """List all courses."""
    result = await session.execute(
        select(Course).offset(skip).limit(limit)
    )
    courses = result.scalars().all()
    return [CourseReadAdmin.model_validate(c) for c in courses]


@router.get("/courses/{course_id}", response_model=CourseReadAdmin)
async def get_course_endpoint(
    course_id: str,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Get a specific course."""
    course = await session.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return CourseReadAdmin.model_validate(course)


@router.patch("/courses/{course_id}", response_model=CourseReadAdmin)
async def update_course_endpoint(
    course_id: str,
    data: CourseUpdateAdmin,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Update a course."""
    course = await update_course_admin(
        session,
        admin_id=admin.id,
        course_id=course_id,
        update_data=data.model_dump(exclude_unset=True),
    )
    return CourseReadAdmin.model_validate(course)


@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course_endpoint(
    course_id: str,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Delete a course."""
    await delete_course_admin(session, admin_id=admin.id, course_id=course_id)


# ============================================================================
# Chapter Management
# ============================================================================

@router.post("/courses/{course_id}/chapters", response_model=ChapterReadAdmin, status_code=status.HTTP_201_CREATED)
async def create_chapter_endpoint(
    course_id: str,
    data: ChapterCreateAdmin,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Create a new chapter in a course."""
    chapter = await create_chapter_admin(
        session,
        admin_id=admin.id,
        course_id=course_id,
        **data.model_dump(),
    )
    return ChapterReadAdmin.model_validate(chapter)


@router.get("/courses/{course_id}/chapters", response_model=List[ChapterReadAdmin])
async def list_chapters_endpoint(
    course_id: str,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """List all chapters in a course."""
    result = await session.execute(
        select(Chapter).where(Chapter.course_id == course_id)
    )
    chapters = result.scalars().all()
    return [ChapterReadAdmin.model_validate(c) for c in chapters]


@router.get("/chapters/{chapter_id}", response_model=ChapterReadAdmin)
async def get_chapter_endpoint(
    chapter_id: str,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Get a specific chapter."""
    chapter = await session.get(Chapter, chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return ChapterReadAdmin.model_validate(chapter)


@router.patch("/chapters/{chapter_id}", response_model=ChapterReadAdmin)
async def update_chapter_endpoint(
    chapter_id: str,
    data: ChapterUpdateAdmin,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Update a chapter."""
    chapter = await update_chapter_admin(
        session,
        admin_id=admin.id,
        chapter_id=chapter_id,
        update_data=data.model_dump(exclude_unset=True),
    )
    return ChapterReadAdmin.model_validate(chapter)


@router.delete("/chapters/{chapter_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chapter_endpoint(
    chapter_id: str,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Delete a chapter."""
    await delete_chapter_admin(session, admin_id=admin.id, chapter_id=chapter_id)


# ============================================================================
# Lesson Management
# ============================================================================

@router.post("/chapters/{chapter_id}/lessons", response_model=LessonReadAdmin, status_code=status.HTTP_201_CREATED)
async def create_lesson_endpoint(
    chapter_id: str,
    data: LessonCreateAdmin,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Create a new lesson in a chapter."""
    # Get chapter to find course_id
    chapter = await session.get(Chapter, chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    lesson = await create_lesson_admin(
        session,
        admin_id=admin.id,
        chapter_id=chapter_id,
        course_id=chapter.course_id,
        **data.model_dump(),
    )
    return LessonReadAdmin.model_validate(lesson)


@router.get("/chapters/{chapter_id}/lessons", response_model=List[LessonReadAdmin])
async def list_lessons_endpoint(
    chapter_id: str,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """List all lessons in a chapter."""
    result = await session.execute(
        select(Lesson).where(Lesson.chapter_id == chapter_id)
    )
    lessons = result.scalars().all()
    return [LessonReadAdmin.model_validate(l) for l in lessons]


@router.get("/lessons/{lesson_id}", response_model=LessonReadAdmin)
async def get_lesson_endpoint(
    lesson_id: str,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Get a specific lesson."""
    lesson = await session.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return LessonReadAdmin.model_validate(lesson)


@router.patch("/lessons/{lesson_id}", response_model=LessonReadAdmin)
async def update_lesson_endpoint(
    lesson_id: str,
    data: LessonUpdateAdmin,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Update a lesson."""
    lesson = await update_lesson_admin(
        session,
        admin_id=admin.id,
        lesson_id=lesson_id,
        update_data=data.model_dump(exclude_unset=True),
    )
    return LessonReadAdmin.model_validate(lesson)


@router.delete("/lessons/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lesson_endpoint(
    lesson_id: str,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Delete a lesson."""
    await delete_lesson_admin(session, admin_id=admin.id, lesson_id=lesson_id)


# ============================================================================
# Quiz & Question Management
# ============================================================================

@router.post("/chapters/{chapter_id}/quiz", response_model=QuizReadAdmin, status_code=status.HTTP_201_CREATED)
async def create_quiz_endpoint(
    chapter_id: str,
    data: QuizCreateAdmin,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Create a quiz for a chapter."""
    # Get chapter to find course_id
    chapter = await session.get(Chapter, chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    quiz = await create_quiz_admin(
        session,
        admin_id=admin.id,
        chapter_id=chapter_id,
        course_id=chapter.course_id,
        **data.model_dump(),
    )
    return QuizReadAdmin.model_validate(quiz)


@router.get("/quizzes/{quiz_id}", response_model=QuizReadAdmin)
async def get_quiz_endpoint(
    quiz_id: str,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Get a specific quiz."""
    quiz = await session.get(Quiz, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return QuizReadAdmin.model_validate(quiz)


@router.patch("/quizzes/{quiz_id}", response_model=QuizReadAdmin)
async def update_quiz_endpoint(
    quiz_id: str,
    data: QuizUpdateAdmin,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Update a quiz."""
    quiz = await update_quiz_admin(
        session,
        admin_id=admin.id,
        quiz_id=quiz_id,
        update_data=data.model_dump(exclude_unset=True),
    )
    return QuizReadAdmin.model_validate(quiz)


@router.post("/quizzes/{quiz_id}/questions", response_model=QuestionReadAdmin, status_code=status.HTTP_201_CREATED)
async def create_question_endpoint(
    quiz_id: str,
    data: QuestionCreateAdmin,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Create a question for a quiz."""
    question = await create_question_admin(
        session,
        admin_id=admin.id,
        quiz_id=quiz_id,
        **data.model_dump(),
    )
    return QuestionReadAdmin.model_validate(question)


@router.get("/quizzes/{quiz_id}/questions", response_model=List[QuestionReadAdmin])
async def list_questions_endpoint(
    quiz_id: str,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """List all questions in a quiz."""
    result = await session.execute(
        select(Question).where(Question.quiz_id == quiz_id)
    )
    questions = result.scalars().all()
    return [QuestionReadAdmin.model_validate(q) for q in questions]


@router.patch("/questions/{question_id}", response_model=QuestionReadAdmin)
async def update_question_endpoint(
    question_id: str,
    data: QuestionUpdateAdmin,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Update a quiz question."""
    question = await update_question_admin(
        session,
        admin_id=admin.id,
        question_id=question_id,
        update_data=data.model_dump(exclude_unset=True),
    )
    return QuestionReadAdmin.model_validate(question)


@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question_endpoint(
    question_id: str,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Delete a quiz question."""
    await delete_question_admin(session, admin_id=admin.id, question_id=question_id)


# ============================================================================
# Assignment Management
# ============================================================================

@router.post("/courses/{course_id}/assignments", response_model=AssignmentReadAdmin, status_code=status.HTTP_201_CREATED)
async def create_assignment_endpoint(
    course_id: str,
    data: AssignmentCreateAdmin,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Create an assignment for a course."""
    assignment = await create_assignment_admin(
        session,
        admin_id=admin.id,
        course_id=course_id,
        **data.model_dump(),
    )
    return AssignmentReadAdmin.model_validate(assignment)


@router.get("/courses/{course_id}/assignments", response_model=List[AssignmentReadAdmin])
async def list_assignments_endpoint(
    course_id: str,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """List all assignments for a course."""
    result = await session.execute(
        select(Assignment).where(Assignment.course_id == course_id)
    )
    assignments = result.scalars().all()
    return [AssignmentReadAdmin.model_validate(a) for a in assignments]


@router.get("/assignments/{assignment_id}", response_model=AssignmentReadAdmin)
async def get_assignment_endpoint(
    assignment_id: str,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Get a specific assignment."""
    assignment = await session.get(Assignment, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return AssignmentReadAdmin.model_validate(assignment)


@router.patch("/assignments/{assignment_id}", response_model=AssignmentReadAdmin)
async def update_assignment_endpoint(
    assignment_id: str,
    data: AssignmentUpdateAdmin,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Update an assignment."""
    assignment = await update_assignment_admin(
        session,
        admin_id=admin.id,
        assignment_id=assignment_id,
        update_data=data.model_dump(exclude_unset=True),
    )
    return AssignmentReadAdmin.model_validate(assignment)


@router.delete("/assignments/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assignment_endpoint(
    assignment_id: str,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Delete an assignment."""
    await delete_assignment_admin(session, admin_id=admin.id, assignment_id=assignment_id)


# ============================================================================
# Project Management
# ============================================================================

@router.post("/courses/{course_id}/projects", response_model=ProjectReadAdmin, status_code=status.HTTP_201_CREATED)
async def create_project_endpoint(
    course_id: str,
    data: ProjectCreateAdmin,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Create a project for a course."""
    project = await create_project_admin(
        session,
        admin_id=admin.id,
        course_id=course_id,
        **data.model_dump(),
    )
    return ProjectReadAdmin.model_validate(project)


@router.get("/courses/{course_id}/projects", response_model=List[ProjectReadAdmin])
async def list_projects_endpoint(
    course_id: str,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """List all projects for a course."""
    result = await session.execute(
        select(Project).where(Project.course_id == course_id)
    )
    projects = result.scalars().all()
    return [ProjectReadAdmin.model_validate(p) for p in projects]


@router.get("/projects/{project_id}", response_model=ProjectReadAdmin)
async def get_project_endpoint(
    project_id: str,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Get a specific project."""
    project = await session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectReadAdmin.model_validate(project)


@router.patch("/projects/{project_id}", response_model=ProjectReadAdmin)
async def update_project_endpoint(
    project_id: str,
    data: ProjectUpdateAdmin,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Update a project."""
    project = await update_project_admin(
        session,
        admin_id=admin.id,
        project_id=project_id,
        update_data=data.model_dump(exclude_unset=True),
    )
    return ProjectReadAdmin.model_validate(project)


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_endpoint(
    project_id: str,
    session: AsyncSession = Depends(get_session),
    admin: AdminUser = Depends(get_current_admin),
):
    """Delete a project."""
    await delete_project_admin(session, admin_id=admin.id, project_id=project_id)


# ============================================================================
# Audit Logs
# ============================================================================

@router.get("/audit-logs", response_model=List[AuditLogRead])
async def get_audit_logs_endpoint(
    entity_type: Optional[str] = None,
    admin_id: Optional[str] = None,
    action: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
    current_admin: AdminUser = Depends(get_current_admin),
):
    """Get audit logs with optional filters."""
    from typing import Optional
    
    action_enum = None
    if action:
        try:
            action_enum = AuditActionType[action.upper()]
        except KeyError:
            raise HTTPException(status_code=400, detail="Invalid action type")

    logs = await get_audit_logs(
        session,
        entity_type=entity_type,
        admin_id=admin_id,
        action=action_enum,
        limit=limit,
        offset=offset,
    )
    return [AuditLogRead.model_validate(log) for log in logs]
