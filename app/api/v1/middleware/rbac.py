"""app/api/v1/middleware/rbac.py - Global RBAC enforcement middleware."""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.core.security import decode_token_with_role
import structlog

logger = structlog.get_logger()


class AdminRBACMiddleware(BaseHTTPMiddleware):
    """
    Global RBAC middleware to enforce admin-only access on admin routes.
    Blocks non-admin requests to /api/v1/admin/* with 403 Forbidden.
    """

    ADMIN_ROUTE_PREFIX = "/api/v1/admin"
    PUBLIC_PATHS = [
        "/api/v1/admin/login",  # Allow login for all
    ]

    async def dispatch(self, request: Request, call_next):
        """Intercept request, validate RBAC for admin routes."""
        
        # Only enforce on admin routes
        if not request.url.path.startswith(self.ADMIN_ROUTE_PREFIX):
            return await call_next(request)
        
        # Allow public admin paths (login)
        if request.url.path in self.PUBLIC_PATHS:
            return await call_next(request)

        # Extract and validate token
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            logger.warning(
                "admin_rbac_denied",
                path=request.url.path,
                reason="missing_token",
            )
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing authentication token"},
            )

        try:
            # Extract Bearer token
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                raise ValueError("Invalid auth scheme")
        except (ValueError, AttributeError):
            logger.warning(
                "admin_rbac_denied",
                path=request.url.path,
                reason="invalid_token_format",
            )
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid authorization header"},
            )

        # Decode token
        payload = decode_token_with_role(token)
        if not payload:
            logger.warning(
                "admin_rbac_denied",
                path=request.url.path,
                reason="invalid_token",
            )
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid or expired token"},
            )

        # Enforce admin role
        user_role = payload.get("role")
        if user_role != "admin":
            logger.warning(
                "admin_rbac_denied",
                path=request.url.path,
                user_id=payload.get("sub"),
                user_role=user_role,
                reason="insufficient_privileges",
            )
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "detail": "Admin access required. This operation is restricted to administrators only."
                },
            )

        # Allow the request to proceed
        return await call_next(request)
