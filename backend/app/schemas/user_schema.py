from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    age: int
    biological_sex: str
    height_cm: float
    weight_kg: float
    wrist_cm: Optional[float] = None
    ankle_cm: Optional[float] = None
    waist_cm: Optional[float] = None
    hip_cm: Optional[float] = None
    neck_cm: Optional[float] = None
    known_body_fat_pct: Optional[float] = None
    experience_level: str
    training_years: Optional[str] = None
    days_available: int = Field(..., ge=1, le=6)
    session_duration: Optional[str] = None
    skip_frequency: str
    follows_progressive_overload: Optional[str] = None
    sleep_hours: Optional[str] = None
    stress_level: Optional[str] = None
    job_activity: Optional[str] = None
    diet_quality: Optional[str] = None
    diet_strictness: str
    dietary_preference: Optional[str] = None
    foods_to_avoid: Optional[str] = None
    meals_per_day: Optional[str] = None
    uses_supplements: Optional[str] = None
    primary_goal: str
    timeline_preference: Optional[str] = None
    ideal_physique: Optional[str] = None
    biggest_struggle: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    name: str
    age: int
    biological_sex: str
    height_cm: float
    weight_kg: float
    experience_level: str
    days_available: int
    primary_goal: str
    consistency_score: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True
