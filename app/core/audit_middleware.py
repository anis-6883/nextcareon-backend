"""
Audit logging middleware for FastAPI.
Automatically logs all admin API calls to the AdminAuditLog table.
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import json
import logging
from typing import Callable

from app.core.config import settings
from app.db.session import SessionLocal
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)


class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that automatically logs admin API calls.
    Attached to admin routes specifically to avoid logging regular user traffic.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request, execute it, and log if it's an admin action.
        """
        if not settings.ADMIN_ENABLE_AUDIT_LOGGING:
            return await call_next(request)

        # Extract request metadata
        ip_address = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "Unknown")
        path = request.url.path
        method = request.method

        # Try to extract admin_id from JWT token (set by auth dependency)
        admin_id = None
        user = getattr(request.state, "user", None)
        if user:
            admin_id = getattr(user, "user_id", None)

        # Execute the request
        response = await call_next(request)

        # Determine action type from endpoint and method
        action_type = self._determine_action_type(path, method)
        if not action_type:
            return response

        # Extract target_id from request if possible
        target_id = None
        target_type = None
        try:
            if method in ["PUT", "PATCH", "DELETE"] and "/admin/" in path:
                # Try to extract ID from URL path or body
                path_parts = path.split("/")
                for part in path_parts:
                    if part.isdigit():
                        target_id = int(part)
                        break

            # Determine target type from path
            if "/courses" in path:
                target_type = "COURSE"
            elif "/skills" in path:
                target_type = "SKILL"
            elif "/projects" in path:
                target_type = "PROJECT"
            elif "/resources" in path:
                target_type = "RESOURCE"
            elif "/users" in path:
                target_type = "USER"
            elif "/warnings" in path:
                target_type = "WARNING"
        except Exception as e:
            logger.warning(f"Could not extract target info from request: {e}")

        # Log the action asynchronously (fire and forget)
        try:
            self._log_audit_action(
                admin_id=admin_id,
                action_type=action_type,
                target_type=target_type,
                target_id=target_id,
                status="success" if 200 <= response.status_code < 300 else "failed",
                ip_address=ip_address,
                user_agent=user_agent,
                response_status=response.status_code,
            )
        except Exception as e:
            logger.error(f"Failed to log audit action: {e}")

        return response

    @staticmethod
    def _get_client_ip(request: Request) -> str:
        """Extract client IP address from request, accounting for proxies."""
        # Check for X-Forwarded-For header (set by proxies)
        x_forwarded_for = request.headers.get("x-forwarded-for")
        if x_forwarded_for:
            # Use the first IP in the list (original client)
            return x_forwarded_for.split(",")[0].strip()

        # Fallback to direct connection
        return request.client.host if request.client else "Unknown"

    @staticmethod
    def _determine_action_type(path: str, method: str) -> str:
        """
        Determine action type from request path and method.
        Returns action type string or None if not an admin action.
        """
        action_map = {
            # Courses
            "/admin/courses": {
                "POST": "COURSE_CREATED",
                "PUT": "COURSE_UPDATED",
                "DELETE": "COURSE_DELETED",
            },
            # Skills
            "/admin/skills": {
                "POST": "SKILL_CREATED",
                "PUT": "SKILL_UPDATED",
                "DELETE": "SKILL_DELETED",
            },
            # Projects
            "/admin/projects": {
                "POST": "PROJECT_CREATED",
                "PUT": "PROJECT_UPDATED",
                "DELETE": "PROJECT_DELETED",
            },
            # Resources
            "/admin/resources": {
                "POST": "RESOURCE_CREATED",
                "PUT": "RESOURCE_UPDATED",
                "DELETE": "RESOURCE_DELETED",
            },
            # Users
            "/admin/users": {
                "PUT": "USER_UPDATED",
            },
            "/admin/users/ban": {
                "POST": "USER_BANNED",
            },
            "/admin/users/suspend": {
                "POST": "USER_SUSPENDED",
            },
            "/admin/users/unsuspend": {
                "POST": "USER_UNSUSPENDED",
            },
            # Warnings
            "/admin/warnings": {
                "POST": "USER_WARNED",
                "PUT": "WARNING_UPDATED",
            },
            "/admin/warnings/acknowledge": {
                "POST": "WARNING_ACKNOWLEDGED",
            },
        }

        # Find matching action
        for route_prefix, methods in action_map.items():
            if route_prefix in path:
                return methods.get(method)

        return None

    @staticmethod
    def _log_audit_action(
        admin_id: int = None,
        action_type: str = None,
        target_type: str = None,
        target_id: int = None,
        status: str = "success",
        ip_address: str = None,
        user_agent: str = None,
        response_status: int = None,
        error_message: str = None,
    ):
        """Log an action to the audit database."""
        if admin_id is None:
            return  # Don't log unauthenticated requests

        details = {
            "response_status": response_status,
            "timestamp_logged": str(datetime.utcnow()),
        }

        session = SessionLocal()
        try:
            AuditService.log_action(
                session=session,
                admin_id=admin_id,
                action_type=action_type,
                target_type=target_type,
                target_id=target_id,
                details=details,
                status=status,
                error_message=error_message,
                ip_address=ip_address,
                user_agent=user_agent,
            )
        finally:
            session.close()


# Import datetime at the end to avoid circular imports
from datetime import datetime
