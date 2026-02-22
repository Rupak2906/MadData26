from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Timeline(Base):
    __tablename__ = "timeline"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Overall timeline estimates
    total_months_optimistic = Column(Integer, nullable=True)
    total_months_realistic = Column(Integer, nullable=True)
    total_months_conservative = Column(Integer, nullable=True)
    confidence_level = Column(String, nullable=True)  # low / medium / high

    # Consistency impact message
    consistency_score = Column(Float, nullable=True)
    consistency_impact = Column(String, nullable=True)  # "Increasing to 80% saves 4 months"

    # Phase breakdown
    phase_1_goal = Column(String, nullable=True)      # e.g. Fat Loss
    phase_1_months = Column(Integer, nullable=True)
    phase_2_goal = Column(String, nullable=True)      # e.g. Muscle Building
    phase_2_months = Column(Integer, nullable=True)
    phase_3_goal = Column(String, nullable=True)      # e.g. Peak Refinement
    phase_3_months = Column(Integer, nullable=True)

    # Milestones
    milestone_1_month = Column(Integer, nullable=True)
    milestone_1_description = Column(String, nullable=True)
    milestone_2_month = Column(Integer, nullable=True)
    milestone_2_description = Column(String, nullable=True)
    milestone_3_month = Column(Integer, nullable=True)
    milestone_3_description = Column(String, nullable=True)

    # Relationship
    user = relationship("User", backref="timelines")

    created_at = Column(DateTime, default=func.now())
