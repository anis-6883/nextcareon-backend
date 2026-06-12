"""app/modules/admin/admin_service.py - Admin CRUD business logic."""

from typing import Optional, List, Dict, Any
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.users.models import Student, AdminUser, UserRole
from app.modules.courses.models import Course, Chapter, Lesson, Quiz, Question, Assignment, Project
from app.modules.gamification.models import Achievement, InventoryItem
from app.core.security import hash_password
from app.core.exceptions import NotFoundException, BadRequestException
from app.modules.admin.audit_service import log_admin_action
from app.modules.admin.audit_models import AuditActionType


# ============================================================================
# User Management
# ============================================================================

async def create_admin_user(
    session: AsyncSession,
    admin_id: str,
    full_name: str,
    email: str,
    password: str,
    role: str = "content_manager",
) -> AdminUser:
    """Create a new admin user."""
    # Check if email already exists
    result = await session.execute(
        select(AdminUser).where(AdminUser.email == email)
    )
    if result.first():
        raise BadRequestException(detail="Email already registered")

    admin_role = UserRole.SUPER_ADMIN if role == "super_admin" else UserRole.CONTENT_MANAGER
    new_admin = AdminUser(
        full_name=full_name,
        email=email,
        password_hash=hash_password(password),
        role=admin_role,
    )
    session.add(new_admin)
    await session.commit()
    await session.refresh(new_admin)

    # Log action
    await log_admin_action(
        session,
        admin_id=admin_id,
        entity_type="AdminUser",
        entity_id=new_admin.id,
        action=AuditActionType.CREATE,
        after_state={"email": new_admin.email, "role": new_admin.role},
        reason="Created new admin user",
    )

    return new_admin


async def update_admin_user(
    session: AsyncSession,
    admin_id: str,
    target_admin_id: str,
    update_data: Dict[str, Any],
) -> AdminUser:
    """Update an admin user."""
    admin = await session.get(AdminUser, target_admin_id)
    if not admin:
        raise NotFoundException(resource="Admin User")

    before_state = {"full_name": admin.full_name, "role": admin.role}

    for field, value in update_data.items():
        if field == "role":
            setattr(admin, field, UserRole[value.upper()])
        else:
            setattr(admin, field, value)

    await session.commit()
    await session.refresh(admin)

    after_state = {"full_name": admin.full_name, "role": admin.role}

    await log_admin_action(
        session,
        admin_id=admin_id,
        entity_type="AdminUser",
        entity_id=target_admin_id,
        action=AuditActionType.UPDATE,
        before_state=before_state,
        after_state=after_state,
        reason="Updated admin user",
    )

    return admin


async def delete_admin_user(
    session: AsyncSession,
    admin_id: str,
    target_admin_id: str,
) -> None:
    """Delete an admin user."""
    admin = await session.get(AdminUser, target_admin_id)
    if not admin:
        raise NotFoundException(resource="Admin User")

    await log_admin_action(
        session,
        admin_id=admin_id,
        entity_type="AdminUser",
        entity_id=target_admin_id,
        action=AuditActionType.DELETE,
        before_state={"email": admin.email, "role": admin.role},
        reason="Deleted admin user",
    )

    await session.delete(admin)
    await session.commit()


async def get_all_admin_users(session: AsyncSession, limit: int = 100, offset: int = 0) -> list:
    """Get all admin users."""
    result = await session.execute(
        select(AdminUser).offset(offset).limit(limit)
    )
    return result.scalars().all()


# ============================================================================
# Student Management
# ============================================================================

async def create_student_admin(
    session: AsyncSession,
    admin_id: str,
    full_name: str,
    email: str,
    password: str,
    **kwargs,
) -> Student:
    """Create a new student (admin operation)."""
    # Check if email already exists
    result = await session.execute(
        select(Student).where(Student.email == email)
    )
    if result.first():
        raise BadRequestException(detail="Email already registered")

    student = Student(
        full_name=full_name,
        email=email,
        password_hash=hash_password(password),
        **kwargs,
    )
    session.add(student)
    await session.commit()
    await session.refresh(student)

    await log_admin_action(
        session,
        admin_id=admin_id,
        entity_type="Student",
        entity_id=student.id,
        action=AuditActionType.CREATE,
        after_state={"email": student.email, "full_name": student.full_name},
        reason="Created new student account",
    )

    return student


async def update_student_admin(
    session: AsyncSession,
    admin_id: str,
    student_id: str,
    update_data: Dict[str, Any],
) -> Student:
    """Update a student (admin operation)."""
    student = await session.get(Student, student_id)
    if not student:
        raise NotFoundException(resource="Student")

    before_state = {
        "full_name": student.full_name,
        "xp_points": student.xp_points,
        "coins": student.coins,
    }

    for field, value in update_data.items():
        if hasattr(student, field):
            setattr(student, field, value)

    await session.commit()
    await session.refresh(student)

    after_state = {
        "full_name": student.full_name,
        "xp_points": student.xp_points,
        "coins": student.coins,
    }

    await log_admin_action(
        session,
        admin_id=admin_id,
        entity_type="Student",
        entity_id=student_id,
        action=AuditActionType.UPDATE,
        before_state=before_state,
        after_state=after_state,
        reason="Updated student profile",
    )

    return student


async def delete_student_admin(
    session: AsyncSession,
    admin_id: str,
    student_id: str,
) -> None:
    """Delete a student (admin operation)."""
    student = await session.get(Student, student_id)
    if not student:
        raise NotFoundException(resource="Student")

    await log_admin_action(
        session,
        admin_id=admin_id,
        entity_type="Student",
        entity_id=student_id,
        action=AuditActionType.DELETE,
        before_state={"email": student.email, "full_name": student.full_name},
        reason="Deleted student account",
    )

    await session.delete(student)
    await session.commit()


# ============================================================================
# Course Management
# ============================================================================

async def create_course_admin(
    session: AsyncSession,
    admin_id: str,
    title: str,
    slug: str,
    **kwargs,
) -> Course:
    """Create a new course (admin operation)."""
    # Check slug uniqueness
    result = await session.execute(
        select(Course).where(Course.slug == slug)
    )
    if result.first():
        raise BadRequestException(detail="Course slug already exists")

    course = Course(title=title, slug=slug, **kwargs)
    session.add(course)
    await session.commit()
    await session.refresh(course)

    await log_admin_action(
        session,
        admin_id=admin_id,
        entity_type="Course",
        entity_id=course.id,
        action=AuditActionType.CREATE,
        after_state={"title": course.title, "slug": course.slug},
        reason="Created new course",
    )

    return course


async def update_course_admin(
    session: AsyncSession,
    admin_id: str,
    course_id: str,
    update_data: Dict[str, Any],
) -> Course:
    """Update a course (admin operation)."""
    course = await session.get(Course, course_id)
    if not course:
        raise NotFoundException(resource="Course")

    before_state = {"title": course.title, "slug": course.slug}

    for field, value in update_data.items():
        if hasattr(course, field):
            setattr(course, field, value)

    await session.commit()
    await session.refresh(course)

    after_state = {"title": course.title, "slug": course.slug}

    await log_admin_action(
        session,
        admin_id=admin_id,
        entity_type="Course",
        entity_id=course_id,
        action=AuditActionType.UPDATE,
        before_state=before_state,
        after_state=after_state,
        reason="Updated course",
    )

    return course


async def delete_course_admin(
    session: AsyncSession,
    admin_id: str,
    course_id: str,
) -> None:
    """Delete a course (admin operation)."""
    course = await session.get(Course, course_id)
    if not course:
        raise NotFoundException(resource="Course")

    await log_admin_action(
        session,
        admin_id=admin_id,
        entity_type="Course",
        entity_id=course_id,
        action=AuditActionType.DELETE,
        before_state={"title": course.title},
        reason="Deleted course",
    )

    await session.delete(course)
    await session.commit()


# ============================================================================
# Chapter Management
# ============================================================================

async def create_chapter_admin(
    session: AsyncSession,
    admin_id: str,
    course_id: str,
    title: str,
    order_index: int,
    **kwargs,
) -> Chapter:
    """Create a new chapter (admin operation)."""
    chapter = Chapter(
        course_id=course_id,
        title=title,
        order_index=order_index,
        **kwargs,
    )
    session.add(chapter)
    await session.commit()
    await session.refresh(chapter)

    await log_admin_action(
        session,
        admin_id=admin_id,
        entity_type="Chapter",
        entity_id=chapter.id,
        action=AuditActionType.CREATE,
        after_state={"title": chapter.title, "course_id": course_id},
        reason="Created new chapter",
    )

    return chapter


async def update_chapter_admin(
    session: AsyncSession,
    admin_id: str,
    chapter_id: str,
    update_data: Dict[str, Any],
) -> Chapter:
    """Update a chapter (admin operation)."""
    chapter = await session.get(Chapter, chapter_id)
    if not chapter:
        raise NotFoundException(resource="Chapter")

    before_state = {"title": chapter.title, "order_index": chapter.order_index}

    for field, value in update_data.items():
        if hasattr(chapter, field):
            setattr(chapter, field, value)

    await session.commit()
    await session.refresh(chapter)

    after_state = {"title": chapter.title, "order_index": chapter.order_index}

    await log_admin_action(
        session,
        admin_id=admin_id,
        entity_type="Chapter",
        entity_id=chapter_id,
        action=AuditActionType.UPDATE,
        before_state=before_state,
        after_state=after_state,
        reason="Updated chapter",
    )

    return chapter


async def delete_chapter_admin(
    session: AsyncSession,
    admin_id: str,
    chapter_id: str,
) -> None:
    """Delete a chapter (admin operation)."""
    chapter = await session.get(Chapter, chapter_id)
    if not chapter:
        raise NotFoundException(resource="Chapter")

    await log_admin_action(
        session,
        admin_id=admin_id,
        entity_type="Chapter",
        entity_id=chapter_id,
        action=AuditActionType.DELETE,
        before_state={"title": chapter.title},
        reason="Deleted chapter",
    )

    await session.delete(chapter)
    await session.commit()


# ============================================================================
# Lesson Management
# ============================================================================

async def create_lesson_admin(
    session: AsyncSession,
    admin_id: str,
    chapter_id: str,
    course_id: str,
    title: str,
    order_index: int,
    **kwargs,
) -> Lesson:
    """Create a new lesson (admin operation)."""
    lesson = Lesson(
        chapter_id=chapter_id,
        course_id=course_id,
        title=title,
        order_index=order_index,
        **kwargs,
    )
    session.add(lesson)
    await session.commit()
    await session.refresh(lesson)

    await log_admin_action(
        session,
        admin_id=admin_id,
        entity_type="Lesson",
        entity_id=lesson.id,
        action=AuditActionType.CREATE,
        after_state={"title": lesson.title, "chapter_id": chapter_id},
        reason="Created new lesson",
    )

    return lesson


async def update_lesson_admin(
    session: AsyncSession,
    admin_id: str,
    lesson_id: str,
    update_data: Dict[str, Any],
) -> Lesson:
    """Update a lesson (admin operation)."""
    lesson = await session.get(Lesson, lesson_id)
    if not lesson:
        raise NotFoundException(resource="Lesson")

    before_state = {"title": lesson.title, "content_text": lesson.content_text[:100]}

    for field, value in update_data.items():
        if hasattr(lesson, field):
            setattr(lesson, field, value)

    await session.commit()
    await session.refresh(lesson)

    after_state = {"title": lesson.title, "content_text": lesson.content_text[:100]}

    await log_admin_action(
        session,
        admin_id=admin_id,
        entity_type="Lesson",
        entity_id=lesson_id,
        action=AuditActionType.UPDATE,
        before_state=before_state,
        after_state=after_state,
        reason="Updated lesson",
    )

    return lesson


async def delete_lesson_admin(
    session: AsyncSession,
    admin_id: str,
    lesson_id: str,
) -> None:
    """Delete a lesson (admin operation)."""
    lesson = await session.get(Lesson, lesson_id)
    if not lesson:
        raise NotFoundException(resource="Lesson")

    await log_admin_action(
        session,
        admin_id=admin_id,
        entity_type="Lesson",
        entity_id=lesson_id,
        action=AuditActionType.DELETE,
        before_state={"title": lesson.title},
        reason="Deleted lesson",
    )

    await session.delete(lesson)
    await session.commit()


# ============================================================================
# Quiz & Question Management
# ============================================================================

async def create_quiz_admin(
    session: AsyncSession,
    admin_id: str,
    chapter_id: str,
    course_id: str,
    **kwargs,
) -> Quiz:
    """Create a new quiz (admin operation)."""
    quiz = Quiz(chapter_id=chapter_id, course_id=course_id, **kwargs)
    session.add(quiz)
    await session.commit()
    await session.refresh(quiz)

    await log_admin_action(
        session,
        admin_id=admin_id,
        entity_type="Quiz",
        entity_id=quiz.id,
        action=AuditActionType.CREATE,
        after_state={"chapter_id": chapter_id},
        reason="Created new quiz",
    )

    return quiz


async def update_quiz_admin(
    session: AsyncSession,
    admin_id: str,
    quiz_id: str,
    update_data: Dict[str, Any],
) -> Quiz:
    """Update a quiz (admin operation)."""
    quiz = await session.get(Quiz, quiz_id)
    if not quiz:
        raise NotFoundException(resource="Quiz")

    before_state = {"pass_score": quiz.pass_score}

    for field, value in update_data.items():
        if hasattr(quiz, field):
            setattr(quiz, field, value)

    await session.commit()
    await session.refresh(quiz)

    after_state = {"pass_score": quiz.pass_score}

    await log_admin_action(
        session,
        admin_id=admin_id,
        entity_type="Quiz",
        entity_id=quiz_id,
        action=AuditActionType.UPDATE,
        before_state=before_state,
        after_state=after_state,
        reason="Updated quiz",
    )

    return quiz


async def create_question_admin(
    session: AsyncSession,
    admin_id: str,
    quiz_id: str,
    question_text: str,
    option_a: str,
    option_b: str,
    option_c: str,
    option_d: str,
    correct_option: str,
) -> Question:
    """Create a new quiz question (admin operation)."""
    question = Question(
        quiz_id=quiz_id,
        question_text=question_text,
        option_a=option_a,
        option_b=option_b,
        option_c=option_c,
        option_d=option_d,
        correct_option=correct_option,
    )
    session.add(question)
    await session.commit()
    await session.refresh(question)

    await log_admin_action(
        session,
        admin_id=admin_id,
        entity_type="Question",
        entity_id=question.id,
        action=AuditActionType.CREATE,
        after_state={"quiz_id": quiz_id, "correct_option": correct_option},
        reason="Created new quiz question",
    )

    return question


async def update_question_admin(
    session: AsyncSession,
    admin_id: str,
    question_id: str,
    update_data: Dict[str, Any],
) -> Question:
    """Update a quiz question (admin operation)."""
    question = await session.get(Question, question_id)
    if not question:
        raise NotFoundException(resource="Question")

    before_state = {"correct_option": question.correct_option}

    for field, value in update_data.items():
        if hasattr(question, field):
            setattr(question, field, value)

    await session.commit()
    await session.refresh(question)

    after_state = {"correct_option": question.correct_option}

    await log_admin_action(
        session,
        admin_id=admin_id,
        entity_type="Question",
        entity_id=question_id,
        action=AuditActionType.UPDATE,
        before_state=before_state,
        after_state=after_state,
        reason="Updated quiz question",
    )

    return question


async def delete_question_admin(
    session: AsyncSession,
    admin_id: str,
    question_id: str,
) -> None:
    """Delete a quiz question (admin operation)."""
    question = await session.get(Question, question_id)
    if not question:
        raise NotFoundException(resource="Question")

    await log_admin_action(
        session,
        admin_id=admin_id,
        entity_type="Question",
        entity_id=question_id,
        action=AuditActionType.DELETE,
        before_state={"question_text": question.question_text},
        reason="Deleted quiz question",
    )

    await session.delete(question)
    await session.commit()


# ============================================================================
# Assignment & Project Management
# ============================================================================

async def create_assignment_admin(
    session: AsyncSession,
    admin_id: str,
    course_id: str,
    title: str,
    **kwargs,
) -> Assignment:
    """Create a new assignment (admin operation)."""
    assignment = Assignment(course_id=course_id, title=title, **kwargs)
    session.add(assignment)
    await session.commit()
    await session.refresh(assignment)

    await log_admin_action(
        session,
        admin_id=admin_id,
        entity_type="Assignment",
        entity_id=assignment.id,
        action=AuditActionType.CREATE,
        after_state={"title": assignment.title},
        reason="Created new assignment",
    )

    return assignment


async def update_assignment_admin(
    session: AsyncSession,
    admin_id: str,
    assignment_id: str,
    update_data: Dict[str, Any],
) -> Assignment:
    """Update an assignment (admin operation)."""
    assignment = await session.get(Assignment, assignment_id)
    if not assignment:
        raise NotFoundException(resource="Assignment")

    before_state = {"title": assignment.title}

    for field, value in update_data.items():
        if hasattr(assignment, field):
            setattr(assignment, field, value)

    await session.commit()
    await session.refresh(assignment)

    after_state = {"title": assignment.title}

    await log_admin_action(
        session,
        admin_id=admin_id,
        entity_type="Assignment",
        entity_id=assignment_id,
        action=AuditActionType.UPDATE,
        before_state=before_state,
        after_state=after_state,
        reason="Updated assignment",
    )

    return assignment


async def delete_assignment_admin(
    session: AsyncSession,
    admin_id: str,
    assignment_id: str,
) -> None:
    """Delete an assignment (admin operation)."""
    assignment = await session.get(Assignment, assignment_id)
    if not assignment:
        raise NotFoundException(resource="Assignment")

    await log_admin_action(
        session,
        admin_id=admin_id,
        entity_type="Assignment",
        entity_id=assignment_id,
        action=AuditActionType.DELETE,
        before_state={"title": assignment.title},
        reason="Deleted assignment",
    )

    await session.delete(assignment)
    await session.commit()


async def create_project_admin(
    session: AsyncSession,
    admin_id: str,
    course_id: str,
    title: str,
    **kwargs,
) -> Project:
    """Create a new project (admin operation)."""
    project = Project(course_id=course_id, title=title, **kwargs)
    session.add(project)
    await session.commit()
    await session.refresh(project)

    await log_admin_action(
        session,
        admin_id=admin_id,
        entity_type="Project",
        entity_id=project.id,
        action=AuditActionType.CREATE,
        after_state={"title": project.title},
        reason="Created new project",
    )

    return project


async def update_project_admin(
    session: AsyncSession,
    admin_id: str,
    project_id: str,
    update_data: Dict[str, Any],
) -> Project:
    """Update a project (admin operation)."""
    project = await session.get(Project, project_id)
    if not project:
        raise NotFoundException(resource="Project")

    before_state = {"title": project.title}

    for field, value in update_data.items():
        if hasattr(project, field):
            setattr(project, field, value)

    await session.commit()
    await session.refresh(project)

    after_state = {"title": project.title}

    await log_admin_action(
        session,
        admin_id=admin_id,
        entity_type="Project",
        entity_id=project_id,
        action=AuditActionType.UPDATE,
        before_state=before_state,
        after_state=after_state,
        reason="Updated project",
    )

    return project


async def delete_project_admin(
    session: AsyncSession,
    admin_id: str,
    project_id: str,
) -> None:
    """Delete a project (admin operation)."""
    project = await session.get(Project, project_id)
    if not project:
        raise NotFoundException(resource="Project")

    await log_admin_action(
        session,
        admin_id=admin_id,
        entity_type="Project",
        entity_id=project_id,
        action=AuditActionType.DELETE,
        before_state={"title": project.title},
        reason="Deleted project",
    )

    await session.delete(project)
    await session.commit()
