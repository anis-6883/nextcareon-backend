from datetime import timedelta
from typing import Optional

from sqlmodel import Session, select

from app.models.user import User
from app.models.admin import Admin
from app.core import security
from app.core.config import settings


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    statement = select(User).where(User.email == email)
    result = db.exec(statement).first()
    if not result:
        return None
    if not security.verify_password(password, result.password):
        return None
    return result


def create_tokens_for_user(user: User) -> dict:
    data = {"sub": str(user.user_id), "email": user.email, "role": user.role}
    access_token = security.create_access_token(data)
    refresh_token = security.create_refresh_token(data)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


def decode_token(token: str) -> dict:
    return security.decode_token(token)


# ---- ADMIN AUTHENTICATION FUNCTIONS ----

def authenticate_admin(db: Session, username: str, password: str) -> Optional[Admin]:
    """Authenticate admin with username and password"""
    statement = select(Admin).where(Admin.username == username)
    result = db.exec(statement).first()
    if not result:
        return None
    if not result.is_active:
        return None
    if not security.verify_password(password, result.password):
        return None
    return result


def create_tokens_for_admin(admin: Admin) -> dict:
    """Create JWT tokens for admin"""
    data = {"sub": str(admin.admin_id), "username": admin.username, "role": "admin"}
    access_token = security.create_access_token(data)
    refresh_token = security.create_refresh_token(data)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


def get_admin_by_id(db: Session, admin_id: int) -> Optional[Admin]:
    """Get admin by admin_id"""
    return db.get(Admin, admin_id)


def get_admin_by_username(db: Session, username: str) -> Optional[Admin]:
    """Get admin by username"""
    statement = select(Admin).where(Admin.username == username)
    return db.exec(statement).first()


def create_admin(db: Session, username: str, password: str, permissions: str = "all") -> Admin:
    """Create new admin user"""
    hashed = security.get_password_hash(password)
    admin = Admin(username=username, password=hashed, permissions=permissions, is_active=True)
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin
