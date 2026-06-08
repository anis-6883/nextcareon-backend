"""app/api/v1/middleware/rate_limiter.py - Global rate limiting middleware."""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from app.core.config import settings


limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.GLOBAL_RATE_LIMIT_STR],
    storage_uri=settings.REDIS_URL,
)


def register_rate_limiter(app: FastAPI):
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded. Please slow down.",
            "retry_after": exc.retry_after,
        },
    )