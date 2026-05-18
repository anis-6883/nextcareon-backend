from pydantic import BaseModel, EmailStr
from typing import Optional


class TokenResponse(BaseModel):
    """Response for login endpoints containing access and refresh tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AdminLogin(BaseModel):
    """Admin login credentials"""
    username: str
    password: str


class AdminRegister(BaseModel):
    """Admin registration payload"""
    username: str
    password: str
    permissions: Optional[str] = "all"


class AdminRead(BaseModel):
    """Admin read schema (does not expose password)"""
    admin_id: int
    username: str
    is_active: bool
    permissions: str

    class Config:
        orm_mode = True
