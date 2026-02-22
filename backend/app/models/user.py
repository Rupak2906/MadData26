from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Basic info
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)   # add this too if missing
    password = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    biological_sex = Column(String, nullable=False)      # male / female

    # Body metrics
    height_cm = Column(Float, nullable=False)
    weight_kg = Column(Float, nullable=False)
    wrist_cm = Column(Float, nullable=True)
    ankle_cm = Column(Float, nullable=True)

    # Circumference measurements
    waist_cm = Column(Float, nullable=True)
    hip_cm = Column(Float, nullable=True)
    neck_cm = Column(Float, nullable=True)
    known_body_fat_pct = Column(Float, nullable=True)    # optional if user knows it

    # Training profile
    experience_level = Column(String, nullable=False)    # beginner / intermediate / advanced
    training_years = Column(String, nullable=True)       # <1yr / 1-3yr / 3yr+
    days_available = Column(Integer, nullable=False)     # 1-6
    session_duration = Column(String, nullable=True)     # 30min / 45min / 60min / 90min+
    skip_frequency = Column(String, nullable=False)      # never / rarely / sometimes / often
    follows_progressive_overload = Column(String, nullable=True)  # yes / no / dont_know

    # Lifestyle
    sleep_hours = Column(String, nullable=True)          # <6hr / 6-7hr / 7-8hr / 8hr+
    stress_level = Column(String, nullable=True)         # low / moderate / high
    job_activity = Column(String, nullable=True)         # active / moderate / sedentary

    # Nutrition
    diet_quality = Column(String, nullable=True)         # poor / average / good / very_clean
    diet_strictness = Column(String, nullable=False)     # loose / moderate / strict
    dietary_preference = Column(String, nullable=True)   # none / vegetarian / vegan / keto
    foods_to_avoid = Column(String, nullable=True)       # comma separated
    meals_per_day = Column(String, nullable=True)        # 1-2 / 3 / 4 / 5+
    uses_supplements = Column(String, nullable=True)     # none / protein / creatine / both

    # Goals
    primary_goal = Column(String, nullable=False)        # build_muscle / lose_fat / both
    timeline_preference = Column(String, nullable=True)  # asap / 12mo / 18mo / no_rush
    ideal_physique = Column(String, nullable=True)       # lean_athletic / muscular / v_taper
    biggest_struggle = Column(String, nullable=True)

    # Computed consistency score (calculated from training + lifestyle fields)
    consistency_score = Column(Float, nullable=True)     # 0.0 to 1.0

    created_at = Column(DateTime, default=func.now())
