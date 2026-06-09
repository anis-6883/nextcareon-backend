"""app/core/exceptions.py - Custom HTTP exceptions."""

from fastapi import HTTPException, status


class AuthException(HTTPException):
    """Authentication failed."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenException(HTTPException):
    """Insufficient permissions."""

    def __init__(self, detail: str = "Insufficient permissions") -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class NotFoundException(HTTPException):
    """Resource not found."""

    def __init__(self, resource: str = "Resource") -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"{resource} not found"
        )


class BadRequestException(HTTPException):
    """Bad request."""

    def __init__(self, detail: str = "Bad request") -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class InsufficientCoinsException(HTTPException):
    """Not enough coins for operation."""

    def __init__(self, detail: str = "Insufficient coins") -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
