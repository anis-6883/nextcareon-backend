"""app/api/v1/router.py - Main API router."""

from fastapi import APIRouter
from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.modules.courses.router import router as courses_router
from app.modules.quizzes.router import router as quizzes_router
from app.modules.assignments.router import router as assignments_router
from app.modules.portfolio.router import router as portfolio_router
from app.modules.career_paths.router import router as career_paths_router
from app.modules.career_explorer.router import router as career_explorer_router
from app.modules.admin.router import router as admin_router
from app.modules.lessons.router import router as lessons_router
from app.modules.career_score.router import router as career_score_router
from app.modules.gamification.router import router as gamification_router
from app.modules.ai_assistant.router import router as ai_assistant_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(courses_router)
api_router.include_router(quizzes_router)
api_router.include_router(assignments_router)
api_router.include_router(portfolio_router)
api_router.include_router(career_paths_router)
api_router.include_router(career_explorer_router)
api_router.include_router(admin_router)
api_router.include_router(lessons_router)
api_router.include_router(career_score_router)
api_router.include_router(gamification_router)
api_router.include_router(ai_assistant_router)
