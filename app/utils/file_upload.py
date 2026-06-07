"""app/utils/file_upload.py - File upload utilities with validation."""

import os
import uuid
from typing import Optional
from fastapi import UploadFile, HTTPException
from fastapi.responses import JSONResponse

ALLOWED_MIME_TYPES = {
    "image/jpeg", "image/png", "image/gif", "image/webp",
    "application/pdf",
    "text/plain", "text/markdown",
    "application/json",
    "video/mp4", "video/webm",
    "audio/mpeg", "audio/wav", "audio/ogg",
}

MAX_FILE_SIZE = 50 * 1024 * 1024

STORAGE_BASE_PATH = "app/uploads"


def get_allowed_extensions_for_mime():
    return {
        "image/jpeg": {".jpg", ".jpeg"},
        "image/png": {".png"},
        "image/gif": {".gif"},
        "image/webp": {".webp"},
        "application/pdf": {".pdf"},
        "text/plain": {".txt"},
        "text/markdown": {".md"},
        "application/json": {".json"},
        "video/mp4": {".mp4"},
        "video/webm": {".webm"},
        "audio/mpeg": {".mp3"},
        "audio/wav": {".wav"},
        "audio/ogg": {".ogg"},
    }


def validate_file(file: UploadFile) -> None:
    if not file.content_type or file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Allowed types: {', '.join(ALLOWED_MIME_TYPES)}"
        )


async def save_upload_file(
    file: UploadFile,
    subfolder: str = "lessons",
    max_size: int = MAX_FILE_SIZE,
) -> str:
    validate_file(file)
    
    content = await file.read()
    if len(content) > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {max_size // (1024*1024)}MB"
        )
    
    ext = os.path.splitext(file.filename or "")[1].lower()
    if not ext:
        for mime_exts in get_allowed_extensions_for_mime().get(file.content_type, []):
            ext = mime_exts
            break
    
    filename = f"{uuid.uuid4()}{ext}"
    upload_dir = os.path.join(STORAGE_BASE_PATH, subfolder)
    os.makedirs(upload_dir, exist_ok=True)
    
    filepath = os.path.join(upload_dir, filename)
    with open(filepath, "wb") as f:
        f.write(content)
    
    return f"/uploads/{subfolder}/{filename}"


async def save_student_submission(
    file: UploadFile,
    student_id: str,
    submission_type: str,
) -> str:
    return await save_upload_file(file, subfolder=f"submissions/{student_id}/{submission_type}")