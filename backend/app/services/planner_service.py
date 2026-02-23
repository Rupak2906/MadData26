"""
planner_service.py
------------------
Combines outputs from the three deterministic plan modules and persists them to the database.
Acts as the bridge between ai_agent.py and the individual plan_service savers.
"""

from sqlalchemy.orm import Session
from app.services.ai_agent import run_full_agent_pipeline
from app.services.plan_service import (
    save_transformation_plan,
    save_dietary_plan,
    save_timeline,
    get_full_plan,
)

# Keys accepted by each DB model
_WORKOUT_KEYS = {
    "peak_lean_mass_kg", "target_bf_pct", "peak_ffmi",
    "muscle_gain_required_kg", "fat_loss_required_pct",
    "muscle_gaps", "primary_strategy", "agent_reasoning",
}
_DIET_KEYS = {
    "tdee", "daily_calories", "caloric_strategy", "caloric_adjustment",
    "protein_g", "carbs_g", "fats_g", "meals_per_day", "meal_complexity",
    "water_intake_liters", "cheat_meals_per_week", "dietary_preference",
    "foods_to_avoid", "diet_reasoning",
}
_TIMELINE_KEYS = {
    "total_months_optimistic", "total_months_realistic", "total_months_conservative",
    "confidence_level", "consistency_score", "consistency_impact",
    "phase_1_goal", "phase_1_months", "phase_2_goal", "phase_2_months",
    "phase_3_goal", "phase_3_months",
    "milestone_1_month", "milestone_1_description",
    "milestone_2_month", "milestone_2_description",
    "milestone_3_month", "milestone_3_description",
}


def generate_and_save_plan(
    db: Session,
    user_id: int,
    user: dict,
    body_analysis: dict,
) -> dict:
    """
    Run full agent pipeline and save all outputs to the DB.

    Returns the saved plan dict (same structure as get_full_plan).
    """
    results = run_full_agent_pipeline(user, body_analysis)

    save_transformation_plan(
        db, user_id,
        {k: v for k, v in results["transformation_plan"].items() if k in _WORKOUT_KEYS}
    )
    save_dietary_plan(
        db, user_id,
        {k: v for k, v in results["dietary_plan"].items() if k in _DIET_KEYS}
    )
    save_timeline(
        db, user_id,
        {k: v for k, v in results["timeline"].items() if k in _TIMELINE_KEYS}
    )

    return get_full_plan(db, user_id)
