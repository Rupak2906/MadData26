from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_jwt_token, verify_jwt_token
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    # Optional at signup; frontend can enrich profile in onboarding.
    age: int = 25
    biological_sex: str = "male"
    height_cm: float = 170.0
    weight_kg: float = 70.0
    experience_level: str = "beginner"
    days_available: int = 3
    skip_frequency: str = "sometimes"
    diet_strictness: str = "moderate"
    primary_goal: str = "both"


class LoginRequest(BaseModel):
    email: str
    password: str


def _user_to_dict(user: User) -> dict:
    return {
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "age": user.age,
        "biological_sex": user.biological_sex,
        "height_cm": user.height_cm,
        "weight_kg": user.weight_kg,
        "experience_level": user.experience_level,
        "primary_goal": user.primary_goal,
        "consistency_score": user.consistency_score,
    }


@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user account and return a JWT."""
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        name=data.name,
        email=data.email,
        password=hash_password(data.password),
        age=data.age,
        biological_sex=data.biological_sex,
        height_cm=data.height_cm,
        weight_kg=data.weight_kg,
        experience_level=data.experience_level,
        days_available=data.days_available,
        skip_frequency=data.skip_frequency,
        diet_strictness=data.diet_strictness,
        primary_goal=data.primary_goal,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_jwt_token(str(user.id))
    return {**_user_to_dict(user), "token": token}


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Login with email/password and return a JWT."""
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="No account found for this email")
    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect password")

    token = create_jwt_token(str(user.id))
    return {**_user_to_dict(user), "token": token}


@router.get("/me")
def get_me(token: str, db: Session = Depends(get_db)):
    """Get current authenticated user."""
    user_id = verify_jwt_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return _user_to_dict(user)
