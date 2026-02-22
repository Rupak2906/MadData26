"""
models.py

SQLAlchemy database models. These define the actual database tables.
Alembic reads these to generate migrations.

"""

from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    # Core
    id                      = Column(Integer, primary_key=True, autoincrement=True)
    name                    = Column(String, nullable=False)
    email                   = Column(String, unique=True, nullable=False)
    password_hash           = Column(String, nullable=False)

    # Body measurements
    age                     = Column(Integer, nullable=False)
    biological_sex          = Column(String, nullable=False)
    height_cm               = Column(Float, nullable=False)
    weight_kg               = Column(Float, nullable=False)
    wrist_cm                = Column(Float, nullable=True)
    ankle_cm                = Column(Float, nullable=True)
    waist_cm                = Column(Float, nullable=True)
    hip_cm                  = Column(Float, nullable=True)
    neck_cm                 = Column(Float, nullable=True)
    known_body_fat_pct      = Column(Float, nullable=True)

    # Training
    experience_level        = Column(String, nullable=False)
    training_years          = Column(String, nullable=True)
    days_available          = Column(Integer, nullable=False)
    session_duration        = Column(String, nullable=True)
    skip_frequency          = Column(String, nullable=False)
    follows_progressive_overload = Column(String, nullable=True)

    # Lifestyle
    sleep_hours             = Column(String, nullable=True)
    stress_level            = Column(String, nullable=True)
    job_activity            = Column(String, nullable=True)

    # Diet
    diet_quality            = Column(String, nullable=True)
    diet_strictness         = Column(String, nullable=False)
    dietary_preference      = Column(String, nullable=True)
    foods_to_avoid          = Column(String, nullable=True)
    meals_per_day           = Column(String, nullable=True)
    uses_supplements        = Column(String, nullable=True)

    # Goals
    primary_goal            = Column(String, nullable=False)
    timeline_preference     = Column(String, nullable=True)
    ideal_physique          = Column(String, nullable=True)
    biggest_struggle        = Column(String, nullable=True)

    # Computed
    consistency_score       = Column(Float, nullable=True)

    # Metadata
    created_at              = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at              = Column(DateTime, default=datetime.utcnow,
                                    onupdate=datetime.utcnow, nullable=False)