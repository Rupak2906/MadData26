from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.core.security import verify_jwt_token
from app.models.user import User

router = APIRouter(prefix="/user", tags=["user"])


def get_current_user(token: str, db: Session) -> User:
    user_id = verify_jwt_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    biological_sex: Optional[str] = None
    experience_level: Optional[str] = None
    days_available: Optional[int] = None
    skip_frequency: Optional[str] = None
    sleep_hours: Optional[str] = None
    stress_level: Optional[str] = None
    diet_strictness: Optional[str] = None
    dietary_preference: Optional[str] = None
    primary_goal: Optional[str] = None
    ideal_physique: Optional[str] = None
    biggest_struggle: Optional[str] = None
    foods_to_avoid: Optional[str] = None
    meals_per_day: Optional[str] = None
    uses_supplements: Optional[str] = None
    training_years: Optional[str] = None
    session_duration: Optional[str] = None
    follows_progressive_overload: Optional[str] = None
    job_activity: Optional[str] = None
    diet_quality: Optional[str] = None
    timeline_preference: Optional[str] = None
    wrist_cm: Optional[float] = None
    ankle_cm: Optional[float] = None
    waist_cm: Optional[float] = None
    hip_cm: Optional[float] = None
    neck_cm: Optional[float] = None
    known_body_fat_pct: Optional[float] = None


@router.get("/profile")
def get_profile(token: str, db: Session = Depends(get_db)):
    """Get user profile."""
    user = get_current_user(token, db)
    return {
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "age": user.age,
        "biological_sex": user.biological_sex,
        "height_cm": user.height_cm,
        "weight_kg": user.weight_kg,
        "experience_level": user.experience_level,
        "days_available": user.days_available,
        "skip_frequency": user.skip_frequency,
        "sleep_hours": user.sleep_hours,
        "stress_level": user.stress_level,
        "diet_strictness": user.diet_strictness,
        "dietary_preference": user.dietary_preference,
        "primary_goal": user.primary_goal,
        "ideal_physique": user.ideal_physique,
        "biggest_struggle": user.biggest_struggle,
        "foods_to_avoid": user.foods_to_avoid,
        "meals_per_day": user.meals_per_day,
        "uses_supplements": user.uses_supplements,
        "training_years": user.training_years,
        "session_duration": user.session_duration,
        "follows_progressive_overload": user.follows_progressive_overload,
        "job_activity": user.job_activity,
        "diet_quality": user.diet_quality,
        "timeline_preference": user.timeline_preference,
        "wrist_cm": user.wrist_cm,
        "ankle_cm": user.ankle_cm,
        "waist_cm": user.waist_cm,
        "hip_cm": user.hip_cm,
        "neck_cm": user.neck_cm,
        "known_body_fat_pct": user.known_body_fat_pct,
        "consistency_score": user.consistency_score,
        "created_at": user.created_at,
    }


@router.patch("/profile")
def update_profile(data: ProfileUpdate, token: str, db: Session = Depends(get_db)):
    """Update user profile."""
    user = get_current_user(token, db)

    for field, value in data.dict(exclude_none=True).items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return {"message": "Profile updated successfully", "user_id": user.id}