"""app/main.py - FastAPI application entry point."""

import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_router
from app.core.exceptions import (
    AuthException,
    ForbiddenException,
    NotFoundException,
    BadRequestException,
    InsufficientCoinsException,
)
from app.api.v1.middleware.rate_limiter import limiter, register_rate_limiter
from app.core.logging import setup_logging


setup_logging()
logger = structlog.get_logger()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

register_rate_limiter(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_PREFIX)


@app.exception_handler(AuthException)
async def auth_exception_handler(request: Request, exc: AuthException):
    logger.warning("auth_error", path=request.url.path, detail=exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(ForbiddenException)
async def forbidden_exception_handler(request: Request, exc: ForbiddenException):
    logger.warning("forbidden_error", path=request.url.path, detail=exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(NotFoundException)
async def not_found_exception_handler(request: Request, exc: NotFoundException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(BadRequestException)
async def bad_request_exception_handler(request: Request, exc: BadRequestException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(InsufficientCoinsException)
async def insufficient_coins_exception_handler(request: Request, exc: InsufficientCoinsException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})