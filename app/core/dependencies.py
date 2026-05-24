"""
Dependency injection functions for FastAPI endpoints.
Handles authentication, authorization, database session management, and request context.
"""

from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlmodel import Session
from datetime import datetime

from app.db.session import get_session
from app.models.admin import Admin
from app.models.user import User
from app.core import security
from app.core.config import settings

security_scheme = HTTPBearer()


class RequestContext:
    """Captures request metadata for audit logging."""
    def __init__(self, request: Request):
        self.ip_address = self._get_client_ip(request)
        self.user_agent = request.headers.get("user-agent", "")
        self.method = request.method
        self.url = str(request.url)
        self.timestamp = datetime.utcnow()

    @staticmethod
    def _get_client_ip(request: Request) -> str:
        """Extract client IP from request, considering proxies."""
        if "x-forwarded-for" in request.headers:
            return request.headers["x-forwarded-for"].split(",")[0].strip()
        return request.client.host if request.client else "unknown"


async def get_request_context(request: Request) -> RequestContext:
    """Dependency to capture request context."""
    return RequestContext(request)


async def get_token(
    credentials = Depends(security_scheme),
) -> Dict[str, Any]:
    """Extract and validate JWT token from Authorization header."""
    token = credentials.credentials
    try:
        payload = security.decode_token(token)
        return payload
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


async def get_current_user(
    token: Dict[str, Any] = Depends(get_token),
    db: Session = Depends(get_session),
) -> User:
    """Dependency to get current authenticated user."""
    user_id = token.get("sub") or token.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token structure")

    try:
        user_id = int(user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid user ID in token")

    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    return user


async def get_current_admin(
    token: Dict[str, Any] = Depends(get_token),
    db: Session = Depends(get_session),
) -> Admin:
    """
    Dependency to get current authenticated admin.
    Validates JWT contains admin role and user is active.
    """
    role = token.get("role")
    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can access this resource",
        )

    admin_id = token.get("sub")
    if not admin_id:
        raise HTTPException(status_code=401, detail="Invalid token structure")

    try:
        admin_id = int(admin_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid admin ID in token")

    admin = db.get(Admin, admin_id)
    if not admin or not admin.is_active:
        raise HTTPException(status_code=403, detail="Admin not found or inactive")

    return admin

