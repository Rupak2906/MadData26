from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class BodyAnalysis(Base):
    __tablename__ = "body_analysis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Image
    image_path = Column(String, nullable=True)

    # Raw measurements from CV pipeline
    shoulder_width_cm = Column(Float, nullable=True)
    hip_width_cm = Column(Float, nullable=True)
    torso_length_cm = Column(Float, nullable=True)
    arm_length_cm = Column(Float, nullable=True)
    leg_length_cm = Column(Float, nullable=True)

    # Derived ratios
    shoulder_hip_ratio = Column(Float, nullable=True)
    chest_to_waist_ratio = Column(Float, nullable=True)
    symmetry_score = Column(Float, nullable=True)

    # Classification
    frame_type = Column(String, nullable=True)        # narrow / balanced / wide
    composition_state = Column(String, nullable=True) # lean / average / overfat
    body_profile = Column(String, nullable=True)      # e.g. wide_lean, narrow_overfat

    # Computed body composition
    body_fat_pct = Column(Float, nullable=True)
    lean_mass_kg = Column(Float, nullable=True)
    ffmi = Column(Float, nullable=True)

    # Relationship
    user = relationship("User", backref="body_analyses")

    created_at = Column(DateTime, default=func.now())
