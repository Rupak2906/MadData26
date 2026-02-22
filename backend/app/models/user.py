from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Auth
    email = Column(String, nullable=True, unique=True)
    password = Column(String, nullable=True)

    # Basic info
    name = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    biological_sex = Column(String, nullable=True)

    # Body metrics
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    wrist_cm = Column(Float, nullable=True)
    ankle_cm = Column(Float, nullable=True)
    waist_cm = Column(Float, nullable=True)
    hip_cm = Column(Float, nullable=True)
    neck_cm = Column(Float, nullable=True)
    known_body_fat_pct = Column(Float, nullable=True)

    # Training profile
    experience_level = Column(String, nullable=True)
    training_years = Column(String, nullable=True)
    days_available = Column(Integer, nullable=True)
    session_duration = Column(String, nullable=True)
    skip_frequency = Column(String, nullable=True)
    follows_progressive_overload = Column(String, nullable=True)

    # Lifestyle
    sleep_hours = Column(String, nullable=True)
    stress_level = Column(String, nullable=True)
    job_activity = Column(String, nullable=True)

    # Nutrition
    diet_quality = Column(String, nullable=True)
    diet_strictness = Column(String, nullable=True)
    dietary_preference = Column(String, nullable=True)
    foods_to_avoid = Column(String, nullable=True)
    meals_per_day = Column(String, nullable=True)
    uses_supplements = Column(String, nullable=True)

    # Goals
    primary_goal = Column(String, nullable=True)
    timeline_preference = Column(String, nullable=True)
    ideal_physique = Column(String, nullable=True)
    biggest_struggle = Column(String, nullable=True)

    # Computed
    consistency_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=func.now())
