from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import time

from app.core.database import get_db
from app.core.security import hash_password, create_jwt_token, verify_jwt_token
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user account."""
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        name=data.name,
        email=data.email,
        password=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_jwt_token(str(user.id), expiration_time=int(time.time()) + 3600)

    return {
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "token": token,
    }


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """User login endpoint."""
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if user.password != hash_password(data.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_jwt_token(str(user.id), expiration_time=int(time.time()) + 3600)

    return {
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "token": token,
    }


@router.get("/me")
def get_me(token: str, db: Session = Depends(get_db)):
    """Get current authenticated user info."""
    user_id = verify_jwt_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
    }