"""app/api/v1/router.py - Main API router."""

from fastapi import APIRouter
from app.modules.users.router import router as users_router
from app.modules.courses.router import router as courses_router
from app.modules.quizzes.router import router as quizzes_router
from app.modules.assignments.router import router as assignments_router
from app.modules.portfolio.router import router as portfolio_router
from app.modules.career_paths.router import router as career_paths_router
from app.modules.admin.router import router as admin_router

api_router = APIRouter()
api_router.include_router(users_router)
api_router.include_router(courses_router)
api_router.include_router(quizzes_router)
api_router.include_router(assignments_router)
api_router.include_router(portfolio_router)
api_router.include_router(career_paths_router)
api_router.include_router(admin_router)