from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime

from app.db.session import get_session
from app.schemas.user import UserCreate, UserRead
from app.schemas.auth_schemas import TokenResponse
from app.schemas.response import StandardResponse
from app.models.user import User
from app.core import security
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=StandardResponse[UserRead], status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_session)):
	"""Register a new user"""
	existing = db.exec(select(User).where(User.email == payload.email)).first()
	if existing:
		raise HTTPException(status_code=400, detail="Email already registered")

	hashed = security.get_password_hash(payload.password)
	user = User(name=payload.name, email=payload.email, password=hashed, dept=payload.dept, role="user", is_active=True)
	db.add(user)
	db.commit()
	db.refresh(user)
	return StandardResponse(
		status=True,
		message="User registered successfully!",
		data=UserRead.from_orm(user)
	)

@router.post("/login", response_model=StandardResponse[TokenResponse])
def login(form_data: UserCreate, db: Session = Depends(get_session)):
	"""Login with email and password"""
	user = auth_service.authenticate_user(db, form_data.email, form_data.password)
	if not user:
		raise HTTPException(status_code=401, detail="Invalid credentials")
	if not user.is_active:
		raise HTTPException(status_code=403, detail="User account is inactive")

	tokens = auth_service.create_tokens_for_user(user)
	user.last_login = datetime.utcnow()
	db.add(user)
	db.commit()
	return StandardResponse(
		status=True,
		message="User logged in successfully!",
		data=TokenResponse(**tokens)
	)

@router.get("/me", response_model=StandardResponse[UserRead])
def read_me(token: str, db: Session = Depends(get_session)):
	"""Get current user profile"""
	try:
		payload = auth_service.decode_token(token)
	except Exception:
		raise HTTPException(status_code=401, detail="Invalid token")
	user_id = int(payload.get("sub"))
	user = db.get(User, user_id)
	if not user:
		raise HTTPException(status_code=404, detail="User not found")
	return StandardResponse(
		status=True,
		message="User profile fetched successfully!",
		data=UserRead.from_orm(user)
	)
