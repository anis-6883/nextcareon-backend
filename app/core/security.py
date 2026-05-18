from datetime import datetime, timedelta
from typing import Any

from passlib.context import CryptContext
import jwt

from app.core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
	return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
	return pwd_context.hash(password)


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
	to_encode = data.copy()
	expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
	to_encode.update({"exp": expire, "type": "access"})
	encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
	return encoded_jwt


def create_refresh_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
	to_encode = data.copy()
	expire = datetime.utcnow() + (expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
	to_encode.update({"exp": expire, "type": "refresh"})
	encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
	return encoded_jwt


def decode_token(token: str) -> dict[str, Any]:
	return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def check_admin_role(role: str) -> bool:
	"""Verify if role is admin"""
	return role == "admin"


def check_user_role(role: str) -> bool:
	"""Verify if role is user"""
	return role == "user"


def check_token_type(token_data: dict, expected_type: str) -> bool:
	"""Verify token type (access or refresh)"""
	return token_data.get("type") == expected_type
