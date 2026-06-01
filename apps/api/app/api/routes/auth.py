from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import require_admin
from app.core.database import get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models.entities import User
from app.schemas.auth import LoginRequest, TokenOut, UserCreate

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenOut)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenOut:
    user = db.query(User).filter(User.email == payload.email, User.is_active.is_(True)).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenOut(access_token=create_access_token(user.email, user.role), role=user.role)


@router.post("/users", dependencies=[Depends(require_admin)])
def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> dict:
    exists = db.query(User).filter(User.email == payload.email).first()
    if exists:
        raise HTTPException(status_code=409, detail="User already exists")
    user = User(email=payload.email, hashed_password=hash_password(payload.password), role=payload.role)
    db.add(user)
    db.commit()
    return {"id": user.id, "email": user.email, "role": user.role}
