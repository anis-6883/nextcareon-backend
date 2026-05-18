from fastapi import APIRouter

from app.api.v1.endpoints import auth, admin

api_router = APIRouter(prefix="/api/v1")

# User Authentication
api_router.include_router(auth.router)

# Admin Authentication (hidden from public docs)
api_router.include_router(admin.router)
