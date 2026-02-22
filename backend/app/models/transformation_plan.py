from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class TransformationPlan(Base):
    __tablename__ = "transformation_plan"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Peak potential targets
    peak_lean_mass_kg = Column(Float, nullable=True)
    target_bf_pct = Column(Float, nullable=True)
    peak_ffmi = Column(Float, nullable=True)

    # Transformation gaps
    muscle_gain_required_kg = Column(Float, nullable=True)
    fat_loss_required_pct = Column(Float, nullable=True)

    # Per muscle group gaps (stored as JSON)
    # e.g. {"chest": 3.2, "back": 2.8, "legs": 4.5, "arms": 1.4, "shoulders": 1.8}
    muscle_gaps = Column(JSON, nullable=True)

    # Strategy
    primary_strategy = Column(String, nullable=True)  # bulk / cut / recomp

    # Agent reasoning text
    agent_reasoning = Column(String, nullable=True)

    # Relationship
    user = relationship("User", backref="transformation_plans")

    created_at = Column(DateTime, default=func.now())
