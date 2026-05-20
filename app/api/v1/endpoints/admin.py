from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime

from app.db.session import get_session
from app.schemas.auth_schemas import AdminLogin, AdminRegister, AdminRead, TokenResponse
from app.schemas.response import StandardResponse
from app.models.admin import Admin
from app.core import security
from app.services import auth_service

router = APIRouter(prefix="/admin/auth", tags=["admin"], ) # to hide use include_in_schema=False

@router.post("/register", response_model=StandardResponse[AdminRead], status_code=status.HTTP_201_CREATED)
def admin_register(payload: AdminRegister, db: Session = Depends(get_session)):
	"""Register a new admin user (hidden endpoint)"""
	existing = db.exec(select(Admin).where(Admin.username == payload.username)).first()
	if existing:
		raise HTTPException(status_code=400, detail="Username already exists")

	hashed = security.get_password_hash(payload.password)
	admin = Admin(
		username=payload.username,
		password=hashed,
		permissions=payload.permissions,
		is_active=True
	)
	db.add(admin)
	db.commit()
	db.refresh(admin)
	return StandardResponse(
		status=True,
		message="Admin registered successfully!",
		data=AdminRead.from_orm(admin)
	)

@router.post("/login", response_model=StandardResponse[TokenResponse])
def admin_login(payload: AdminLogin, db: Session = Depends(get_session)):
	"""Admin login endpoint (hidden from public docs)"""
	admin = auth_service.authenticate_admin(db, payload.username, payload.password)
	if not admin:
		raise HTTPException(status_code=401, detail="Invalid admin credentials")

	tokens = auth_service.create_tokens_for_admin(admin)
	admin.last_login = datetime.utcnow()
	db.add(admin)
	db.commit()
	return StandardResponse(
		status=True,
		message="Admin logged in successfully!",
		data=TokenResponse(**tokens)
	)

@router.get("/me", response_model=StandardResponse[AdminRead])
def admin_me(token: str, db: Session = Depends(get_session)):
	"""Get current admin profile (hidden endpoint)"""
	try:
		payload = auth_service.decode_token(token)
	except Exception:
		raise HTTPException(status_code=401, detail="Invalid token")

	if payload.get("role") != "admin":
		raise HTTPException(status_code=403, detail="Access denied")

	admin_id = int(payload.get("sub"))
	admin = db.get(Admin, admin_id)
	if not admin:
		raise HTTPException(status_code=404, detail="Admin not found")
	return StandardResponse(
		status=True,
		message="Admin profile fetched successfully!",
		data=AdminRead.from_orm(admin)
	)
