from pydantic import BaseModel, EmailStr
from typing import Optional


class TokenResponse(BaseModel):
    
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AdminLogin(BaseModel):
    
    username: str
    password: str


class AdminRegister(BaseModel):
    
    username: str
    password: str
    permissions: Optional[str] = "all"


class AdminRead(BaseModel):
    
    admin_id: int
    username: str
    is_active: bool
    permissions: str

    class Config:
        from_attributes = True
