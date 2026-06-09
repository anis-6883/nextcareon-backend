"""app/modules/courses/router.py - Course endpoints."""

from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.courses.service import (
    get_courses, get_course_by_id, create_course, update_course, delete_course,
    get_chapters_by_course, create_chapter, get_lessons_by_chapter, create_lesson,
    enroll_student, get_student_dashboard, complete_lesson, generate_certificate,
    get_lesson_tts_audio, get_course_progress
)
from app.modules.courses.schemas import (
    CourseCreate, CourseRead, CourseWithChapters, ChapterCreate, ChapterRead,
    ChapterWithLessons, LessonCreate, LessonRead, LessonComplete
)
from app.modules.courses.models import Course, Chapter, Lesson
from app.db.engine import get_session
from app.core.dependencies import get_current_student, get_current_admin
from app.modules.users.models import Student
from app.utils.file_upload import save_upload_file
from typing import List

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("/", response_model=List[CourseRead])
async def list_courses(
    session: AsyncSession = Depends(get_session),
):
    courses = await get_courses(session)
    return [CourseRead.model_validate(c) for c in courses]


@router.get("/{course_id}", response_model=CourseRead)
async def get_course(
    course_id: str,
    session: AsyncSession = Depends(get_session),
):
    course = await get_course_by_id(session, course_id)
    return CourseRead.model_validate(course)


@router.get("/{course_id}/with-chapters", response_model=CourseWithChapters)
async def get_course_with_chapters(
    course_id: str,
    session: AsyncSession = Depends(get_session),
):
    course = await get_course_by_id(session, course_id)
    return CourseWithChapters.model_validate(course)


@router.post("/", response_model=CourseRead, status_code=status.HTTP_201_CREATED)
async def create_new_course(
    course: CourseCreate,
    session: AsyncSession = Depends(get_session),
    admin=Depends(get_current_admin),
):
    new_course = await create_course(session, **course.model_dump())
    return CourseRead.model_validate(new_course)


@router.put("/{course_id}", response_model=CourseRead)
async def update_course_endpoint(
    course_id: str,
    course: CourseCreate,
    session: AsyncSession = Depends(get_session),
    admin=Depends(get_current_admin),
):
    updated = await update_course(session, course_id, **course.model_dump())
    return CourseRead.model_validate(updated)


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course_endpoint(
    course_id: str,
    session: AsyncSession = Depends(get_session),
    admin=Depends(get_current_admin),
):
    await delete_course(session, course_id)


@router.get("/{course_id}/chapters", response_model=List[ChapterRead])
async def list_chapters(
    course_id: str,
    session: AsyncSession = Depends(get_session),
):
    chapters = await get_chapters_by_course(session, course_id)
    return [ChapterRead.model_validate(c) for c in chapters]


@router.post("/{course_id}/chapters", response_model=ChapterRead, status_code=status.HTTP_201_CREATED)
async def create_new_chapter(
    course_id: str,
    chapter: ChapterCreate,
    session: AsyncSession = Depends(get_session),
    admin=Depends(get_current_admin),
):
    new_chapter = await create_chapter(session, course_id, **chapter.model_dump())
    return ChapterRead.model_validate(new_chapter)


@router.get("/chapters/{chapter_id}/lessons", response_model=List[LessonRead])
async def list_lessons(
    chapter_id: str,
    session: AsyncSession = Depends(get_session),
):
    lessons = await get_lessons_by_chapter(session, chapter_id)
    return [LessonRead.model_validate(l) for l in lessons]


@router.post("/lessons", response_model=LessonRead, status_code=status.HTTP_201_CREATED)
async def create_new_lesson(
    lesson: LessonCreate,
    session: AsyncSession = Depends(get_session),
    admin=Depends(get_current_admin),
):
    new_lesson = await create_lesson(session, **lesson.model_dump())
    return LessonRead.model_validate(new_lesson)


@router.post("/lessons/{lesson_id}/media", response_model=dict)
async def upload_lesson_media(
    lesson_id: str,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    admin=Depends(get_current_admin),
):
    url = await save_upload_file(file, subfolder="lessons")
    return {"url": url}


@router.post("/{course_id}/enroll", status_code=status.HTTP_201_CREATED)
async def enroll_in_course(
    course_id: str,
    session: AsyncSession = Depends(get_session),
    student: Student = Depends(get_current_student),
):
    await enroll_student(session, student.id, course_id)
    return {"message": "Enrolled successfully"}


@router.get("/dashboard", response_model=dict)
async def student_dashboard(
    session: AsyncSession = Depends(get_session),
    student: Student = Depends(get_current_student),
):
    return await get_student_dashboard(session, student.id)


@router.post("/lessons/complete", status_code=status.HTTP_200_OK)
async def complete_lesson_endpoint(
    lesson_complete: LessonComplete,
    session: AsyncSession = Depends(get_session),
    student: Student = Depends(get_current_student),
):
    return await complete_lesson(session, student.id, lesson_complete.lesson_id)


@router.get("/lessons/{lesson_id}/tts")
async def get_tts(
    lesson_id: str,
    session: AsyncSession = Depends(get_session),
    student: Student = Depends(get_current_student),
):
    return await get_lesson_tts_audio(session, lesson_id)


@router.get("/certificates/{course_id}")
async def get_certificate(
    course_id: str,
    session: AsyncSession = Depends(get_session),
    student: Student = Depends(get_current_student),
):
    return await generate_certificate(session, student.id, course_id)
