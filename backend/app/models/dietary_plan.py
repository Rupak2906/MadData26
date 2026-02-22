from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class DietaryPlan(Base):
    __tablename__ = "dietary_plan"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Caloric strategy
    tdee = Column(Float, nullable=True)
    daily_calories = Column(Integer, nullable=True)
    caloric_strategy = Column(String, nullable=True)    # bulk / cut / recomp
    caloric_adjustment = Column(Integer, nullable=True) # +300 or -400

    # Macros (grams per day)
    protein_g = Column(Integer, nullable=True)
    carbs_g = Column(Integer, nullable=True)
    fats_g = Column(Integer, nullable=True)

    # Meal structure
    meals_per_day = Column(Integer, nullable=True)
    meal_complexity = Column(String, nullable=True)     # simple / moderate / detailed

    # Weekly targets
    water_intake_liters = Column(Float, nullable=True)
    cheat_meals_per_week = Column(Integer, nullable=True)

    # Dietary restrictions
    dietary_preference = Column(String, nullable=True)
    foods_to_avoid = Column(String, nullable=True)

    # Agent reasoning
    diet_reasoning = Column(String, nullable=True)

    # Relationship
    user = relationship("User", backref="dietary_plans")

    created_at = Column(DateTime, default=func.now())
