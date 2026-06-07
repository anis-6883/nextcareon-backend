"""app/modules/courses/service.py - Course business logic."""

import os
from datetime import datetime
from typing import Optional, List
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.courses.models import Course, Chapter, Lesson, LessonProgress, Enrollment, Quiz, QuizAttempt
from app.core.exceptions import NotFoundException, ForbiddenException
from app.cache.redis import redis_client
from app.utils.file_upload import save_upload_file
from io import BytesIO
import tempfile


async def get_course_by_slug(session: AsyncSession, slug: str) -> Optional[Course]:
    result = await session.exec(select(Course).where(Course.slug == slug))
    return result.first()


async def get_course_by_id(session: AsyncSession, course_id: str) -> Course:
    course = await session.get(Course, course_id)
    if not course:
        raise NotFoundException(resource="Course")
    return course


async def get_courses(session: AsyncSession) -> List[Course]:
    result = await session.exec(select(Course).order_by(Course.created_at))
    return result.all()


async def create_course(
    session: AsyncSession,
    title: str,
    slug: str,
    description: str = "",
    difficulty: str = "beginner",
    estimated_hours: int = 0,
) -> Course:
    course = Course(
        title=title,
        slug=slug,
        description=description,
        difficulty=difficulty,
        estimated_hours=estimated_hours,
        total_xp=0,
    )
    session.add(course)
    await session.commit()
    await session.refresh(course)
    return course


async def update_course(
    session: AsyncSession,
    course_id: str,
    **kwargs
) -> Course:
    course = await get_course_by_id(session, course_id)
    for key, value in kwargs.items():
        if hasattr(course, key) and value is not None:
            setattr(course, key, value)
    await session.commit()
    await session.refresh(course)
    return course


async def delete_course(session: AsyncSession, course_id: str) -> None:
    course = await get_course_by_id(session, course_id)
    await session.delete(course)
    await session.commit()


async def get_chapters_by_course(session: AsyncSession, course_id: str) -> List[Chapter]:
    result = await session.exec(
        select(Chapter)
        .where(Chapter.course_id == course_id)
        .order_by(Chapter.order_index)
    )
    return result.all()


async def create_chapter(
    session: AsyncSession,
    course_id: str,
    **kwargs
) -> Chapter:
    course = await get_course_by_id(session, course_id)
    chapter = Chapter(course_id=course_id, **kwargs)
    session.add(chapter)
    await session.commit()
    await session.refresh(chapter)
    return chapter


async def get_lessons_by_chapter(session: AsyncSession, chapter_id: str) -> List[Lesson]:
    result = await session.exec(
        select(Lesson)
        .where(Lesson.chapter_id == chapter_id)
        .order_by(Lesson.order_index)
    )
    return result.all()


async def create_lesson(
    session: AsyncSession,
    course_id: str,
    chapter_id: str,
    **kwargs
) -> Lesson:
    course = await get_course_by_id(session, course_id)
    chapter_result = await session.exec(
        select(Chapter).where(Chapter.id == chapter_id)
    )
    chapter = chapter_result.first()
    if not chapter:
        raise NotFoundException(resource="Chapter")
    
    lesson = Lesson(course_id=course_id, chapter_id=chapter_id, **kwargs)
    session.add(lesson)
    await session.commit()
    await session.refresh(lesson)
    return lesson


async def enroll_student(session: AsyncSession, student_id: str, course_id: str) -> Enrollment:
    existing = await session.exec(
        select(Enrollment).where(
            Enrollment.student_id == student_id,
            Enrollment.course_id == course_id
        )
    )
    if existing.first():
        raise ForbiddenException(detail="Already enrolled in this course")
    
    enrollment = Enrollment(student_id=student_id, course_id=course_id)
    session.add(enrollment)
    await session.commit()
    await session.refresh(enrollment)
    return enrollment


async def get_student_dashboard(session: AsyncSession, student_id: str) -> dict:
    enrollments_result = await session.exec(
        select(Enrollment).where(Enrollment.student_id == student_id)
    )
    enrollments = enrollments_result.all()
    
    courses_data = []
    total_progress = 0
    
    for enrollment in enrollments:
        course = await session.get(Course, enrollment.course_id)
        if not course:
            continue
        
        lessons_result = await session.exec(
            select(Lesson).where(Lesson.course_id == course.id)
        )
        total_lessons = len(lessons_result.all())
        
        progress_result = await session.exec(
            select(LessonProgress).where(
                LessonProgress.student_id == student_id,
                LessonProgress.lesson_id.in_([l.id for l in lessons_result.all()])
            )
        )
        completed_lessons = len(progress_result.all())
        
        progress_pct = round((completed_lessons / total_lessons * 100), 1) if total_lessons > 0 else 0
        total_progress += progress_pct
        
        courses_data.append({
            "id": course.id,
            "title": course.title,
            "enrolled_at": enrollment.enrolled_at,
            "progress": progress_pct,
            "total_lessons": total_lessons,
            "completed_lessons": completed_lessons,
        })
    
    return {
        "enrollments": courses_data,
        "average_progress": round(total_progress / len(enrollments), 1) if enrollments else 0,
        "total_enrollments": len(enrollments),
    }


async def complete_lesson(session: AsyncSession, student_id: str, lesson_id: str) -> dict:
    existing = await session.exec(
        select(LessonProgress).where(
            LessonProgress.student_id == student_id,
            LessonProgress.lesson_id == lesson_id
        )
    )
    if existing.first():
        return {"message": "Lesson already completed", "status": "already_completed"}
    
    lesson = await session.get(Lesson, lesson_id)
    if not lesson:
        raise NotFoundException(resource="Lesson")
    
    progress = LessonProgress(student_id=student_id, lesson_id=lesson_id)
    session.add(progress)
    await session.commit()
    await session.refresh(progress)
    
    return {"message": "Lesson completed", "status": "completed"}


async def get_lesson_tts_audio(session: AsyncSession, lesson_id: str):
    lesson = await session.get(Lesson, lesson_id)
    if not lesson:
        raise NotFoundException(resource="Lesson")
    
    cache_key = f"tts:{lesson_id}"
    cached = await redis_client.get(cache_key)
    if cached:
        return {"audio_url": cached}
    
    from gtts import gTTS
    import uuid
    
    text = lesson.content_text
    if not text:
        raise NotFoundException(resource="Lesson content")
    
    tts = gTTS(text=text, lang='en')
    
    filename = f"{uuid.uuid4()}.mp3"
    upload_dir = "app/uploads/audio"
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, filename)
    
    tts.save(filepath)
    
    audio_url = f"/uploads/audio/{filename}"
    await redis_client.setex(cache_key, 3600, audio_url)
    
    return {"audio_url": audio_url}


async def get_course_progress(session: AsyncSession, student_id: str, course_id: str) -> dict:
    course = await get_course_by_id(session, course_id)
    
    lessons_result = await session.exec(
        select(Lesson).where(Lesson.course_id == course_id)
    )
    lessons = lessons_result.all()
    total_lessons = len(lessons)
    
    progress_result = await session.exec(
        select(LessonProgress).where(
            LessonProgress.student_id == student_id,
            LessonProgress.lesson_id.in_([l.id for l in lessons])
        )
    )
    completed_lessons = len(progress_result.all())
    
    lessons_completed = [p.lesson_id for p in progress_result.all()]
    
    return {
        "course_id": course_id,
        "total_lessons": total_lessons,
        "completed_lessons": completed_lessons,
        "progress_percentage": round((completed_lessons / total_lessons * 100), 1) if total_lessons > 0 else 0,
    }


async def generate_certificate(session: AsyncSession, student_id: str, course_id: str):
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.units import inch
    import uuid
    
    enrollment = await session.exec(
        select(Enrollment).where(
            Enrollment.student_id == student_id,
            Enrollment.course_id == course_id
        )
    )
    enrollment = enrollment.first()
    if not enrollment:
        raise NotFoundException(resource="Enrollment")
    
    course = await session.get(Course, course_id)
    student = await session.get(type('Student', (), {}), student_id)
    from app.modules.users.models import Student as StudentModel
    student = await session.get(StudentModel, student_id)
    
    lessons_result = await session.exec(select(Lesson).where(Lesson.course_id == course_id))
    lessons = lessons_result.all()
    total_lessons = len(lessons)
    
    progress_result = await session.exec(
        select(LessonProgress).where(
            LessonProgress.student_id == student_id,
            LessonProgress.lesson_id.in_([l.id for l in lessons])
        )
    )
    completed_lessons = len(progress_result.all())
    
    quiz_result = await session.exec(
        select(Quiz).where(Quiz.course_id == course_id)
    )
    quizzes = quiz_result.all()
    
    passed_quizzes = 0
    for quiz in quizzes:
        attempt = await session.exec(
            select(QuizAttempt).where(
                QuizAttempt.student_id == student_id,
                QuizAttempt.quiz_id == quiz.id
            )
        )
        attempt = attempt.first()
        if attempt and attempt.passed:
            passed_quizzes += 1
    
    project_result = await session.exec(
        select(StudentProjectSubmission).where(
            StudentProjectSubmission.student_id == student_id,
            StudentProjectSubmission.project_id.in_([p.id for p in await session.exec(select(type('Project', (), {})))])
        )
    )
    
    all_lessons_done = completed_lessons >= total_lessons
    all_quizzes_passed = passed_quizzes >= len(quizzes) if quizzes else True
    
    if not (all_lessons_done and all_quizzes_passed):
        raise ForbiddenException(detail="Course requirements not met for certificate")
    
    filename = f"{uuid.uuid4()}.pdf"
    filepath = os.path.join("app/uploads", "certificates", filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    
    story = []
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1,
        textColor=colors.darkblue
    )
    story.append(Paragraph("Certificate of Completion", title_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph(f"This is to certify that", styles['Normal'], alignment=1))
    story.append(Spacer(1, 10))
    
    student_style = ParagraphStyle('StudentName', parent=styles['Heading2'], alignment=1, textColor=colors.black)
    story.append(Paragraph(student.full_name.upper(), student_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph(f"has successfully completed the course", styles['Normal'], alignment=1))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph(f"<b>{course.title}</b>", styles['Heading3'], alignment=1))
    story.append(Spacer(1, 20))
    
    data = [
        ['Lessons Completed', 'Quizzes Passed', 'Final Project'],
        [str(completed_lessons), str(passed_quizzes), 'Submitted']
    ]
    
    table = Table(data, colWidths=[2 * inch, 2 * inch, 2 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(table)
    story.append(Spacer(1, 20))
    
    story.append(Paragraph(f"Date: {datetime.utcnow().strftime('%B %d, %Y')}", styles['Normal'], alignment=1))
    story.append(Spacer(1, 30))
    
    story.append(Paragraph("_" * 50 + "           " + "_" * 50, styles['Normal']))
    story.append(Paragraph("Signature", styles['Normal'], alignment=1))
    
    doc.build(story)
    
    return {"certificate_url": f"/uploads/certificates/{filename}"}