from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class TransformationPlanResponse(BaseModel):
    id: int
    user_id: int
    peak_lean_mass_kg: Optional[float] = None
    target_bf_pct: Optional[float] = None
    peak_ffmi: Optional[float] = None
    muscle_gain_required_kg: Optional[float] = None
    fat_loss_required_pct: Optional[float] = None
    muscle_gaps: Optional[Dict] = None
    primary_strategy: Optional[str] = None
    agent_reasoning: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class TimelineResponse(BaseModel):
    id: int
    user_id: int
    total_months_optimistic: Optional[int] = None
    total_months_realistic: Optional[int] = None
    total_months_conservative: Optional[int] = None
    confidence_level: Optional[str] = None
    consistency_score: Optional[float] = None
    consistency_impact: Optional[str] = None
    phase_1_goal: Optional[str] = None
    phase_1_months: Optional[int] = None
    phase_2_goal: Optional[str] = None
    phase_2_months: Optional[int] = None
    phase_3_goal: Optional[str] = None
    phase_3_months: Optional[int] = None
    milestone_1_month: Optional[int] = None
    milestone_1_description: Optional[str] = None
    milestone_2_month: Optional[int] = None
    milestone_2_description: Optional[str] = None
    milestone_3_month: Optional[int] = None
    milestone_3_description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class DietaryPlanResponse(BaseModel):
    id: int
    user_id: int
    tdee: Optional[float] = None
    daily_calories: Optional[int] = None
    caloric_strategy: Optional[str] = None
    caloric_adjustment: Optional[int] = None
    protein_g: Optional[int] = None
    carbs_g: Optional[int] = None
    fats_g: Optional[int] = None
    meals_per_day: Optional[int] = None
    meal_complexity: Optional[str] = None
    water_intake_liters: Optional[float] = None
    cheat_meals_per_week: Optional[int] = None
    dietary_preference: Optional[str] = None
    foods_to_avoid: Optional[str] = None
    diet_reasoning: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class FullPlanResponse(BaseModel):
    user_id: int
    transformation_plan: Optional[TransformationPlanResponse] = None
    timeline: Optional[TimelineResponse] = None
    dietary_plan: Optional[DietaryPlanResponse] = None
