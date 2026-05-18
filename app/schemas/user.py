from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    dept: Optional[str] = ""
    role: Optional[str] = "user"


class UserRead(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    role: str
    is_active: bool
    dept: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    name: Optional[str] = None
    dept: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
