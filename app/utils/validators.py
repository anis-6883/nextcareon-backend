"""app/utils/validators.py - Strong password validation."""

import re
from pydantic import field_validator
from pydantic import BaseModel


class PasswordStrengthError(Exception):
    """Raised when password doesn't meet strength requirements."""

    def __init__(self, message: str = "Password does not meet strength requirements"):
        self.message = message
        super().__init__(self.message)


def validate_password_strength(password: str) -> str:
    """
    Validate password meets security requirements.

    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    errors = []

    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter")
    if not re.search(r"\d", password):
        errors.append("Password must contain at least one digit")
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?`~]', password):
        errors.append("Password must contain at least one special character")

    if errors:
        raise PasswordStrengthError("; ".join(errors))

    return password


class StrongPasswordModel(BaseModel):
    """Base model mixin for enforcing strong passwords."""

    password: str

    @field_validator("password")
    @classmethod
    def password_must_be_strong(cls, v: str) -> str:
        return validate_password_strength(v)
