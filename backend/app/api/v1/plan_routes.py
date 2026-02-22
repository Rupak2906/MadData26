from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_jwt_token, resolve_token
from app.core.config import settings
from app.models.body_analysis import BodyAnalysis
from app.models.user import User
from app.models.transformation_plan import TransformationPlan
from app.models.timeline import Timeline
from app.models.dietary_plan import DietaryPlan
from app.services.plan_service import save_transformation_plan, save_timeline, save_dietary_plan
from app.agents.workout_agent import run_workout_agent
from app.agents.diet_agent import run_diet_agent
from app.agents.timeline_agent import run_timeline_agent

router = APIRouter(prefix="/plan", tags=["plan"])


def get_current_user_id(token: Optional[str], authorization: Optional[str]) -> int:
    jwt_token = resolve_token(token, authorization)
    user_id = verify_jwt_token(jwt_token) if jwt_token else None
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return int(user_id)


_WORKOUT_KEYS = [
    "peak_lean_mass_kg", "target_bf_pct", "peak_ffmi",
    "muscle_gain_required_kg", "fat_loss_required_pct",
    "muscle_gaps", "primary_strategy", "agent_reasoning",
]
_DIET_KEYS = [
    "tdee", "daily_calories", "caloric_strategy", "caloric_adjustment",
    "protein_g", "carbs_g", "fats_g", "meals_per_day", "meal_complexity",
    "water_intake_liters", "cheat_meals_per_week", "dietary_preference",
    "foods_to_avoid", "diet_reasoning",
]
_TIMELINE_KEYS = [
    "total_months_optimistic", "total_months_realistic", "total_months_conservative",
    "confidence_level", "consistency_score", "consistency_impact",
    "phase_1_goal", "phase_1_months", "phase_2_goal", "phase_2_months",
    "phase_3_goal", "phase_3_months",
    "milestone_1_month", "milestone_1_description",
    "milestone_2_month", "milestone_2_description",
    "milestone_3_month", "milestone_3_description",
]


def _build_user_dict(user: User) -> dict:
    return {
        "user_id": user.id,
        "name": user.name,
        "age": user.age,
        "biological_sex": user.biological_sex,
        "height_cm": user.height_cm,
        "weight_kg": user.weight_kg,
        "experience_level": user.experience_level,
        "days_available": user.days_available,
        "skip_frequency": user.skip_frequency,
        "diet_strictness": user.diet_strictness,
        "dietary_preference": user.dietary_preference,
        "foods_to_avoid": user.foods_to_avoid,
        "meals_per_day": user.meals_per_day,
        "primary_goal": user.primary_goal,
        "sleep_hours": user.sleep_hours,
        "stress_level": user.stress_level,
        "job_activity": user.job_activity,
        "diet_quality": user.diet_quality,
        "consistency_score": user.consistency_score,
        "uses_supplements": user.uses_supplements,
        "session_duration": user.session_duration,
        "follows_progressive_overload": user.follows_progressive_overload,
    }


def _analysis_from_profile(user: User, analysis: BodyAnalysis | None) -> dict:
    # Prefer latest CV analysis; fall back to profile-derived estimates.
    if analysis:
        return {
            "frame_type": analysis.frame_type or "balanced",
            "body_fat_pct": analysis.body_fat_pct or 18.0,
            "lean_mass_kg": analysis.lean_mass_kg or (user.weight_kg * 0.8),
            "ffmi": analysis.ffmi or 20.0,
            "symmetry_score": analysis.symmetry_score or 0.8,
            "shoulder_hip_ratio": analysis.shoulder_hip_ratio or 1.2,
        }

    height_m = max(user.height_cm / 100.0, 1.2)
    bmi = user.weight_kg / (height_m * height_m)
    sex = 1 if user.biological_sex == "male" else 0
    bf_pct = max(8.0, min(35.0, (1.2 * bmi) + (0.23 * user.age) - (10.8 * sex) - 5.4))
    lean_mass = round(user.weight_kg * (1 - bf_pct / 100), 2)
    ffmi = round(lean_mass / (height_m * height_m), 2)
    return {
        "frame_type": "balanced",
        "body_fat_pct": round(bf_pct, 1),
        "lean_mass_kg": lean_mass,
        "ffmi": ffmi,
        "symmetry_score": 0.8,
        "shoulder_hip_ratio": 1.2,
    }


def _fallback_workout(user: User, analysis: dict) -> dict:
    height_m = max(user.height_cm / 100.0, 1.2)
    peak_ffmi = 24.0 if user.biological_sex == "male" else 20.5
    peak_lean_mass = round(peak_ffmi * (height_m * height_m), 2)
    current_lean = float(analysis.get("lean_mass_kg") or (user.weight_kg * 0.8))
    gain_needed = max(0.0, round(peak_lean_mass - current_lean, 2))
    target_bf = 12.0 if user.primary_goal in {"build_muscle", "both"} else 14.0
    fat_loss = max(0.0, round(float(analysis.get("body_fat_pct", 18.0)) - target_bf, 2))
    return {
        "peak_lean_mass_kg": peak_lean_mass,
        "target_bf_pct": target_bf,
        "peak_ffmi": peak_ffmi,
        "muscle_gain_required_kg": gain_needed,
        "fat_loss_required_pct": fat_loss,
        "muscle_gaps": {"chest": 2.2, "back": 2.0, "legs": 2.8, "arms": 1.4, "shoulders": 1.6},
        "primary_strategy": "recomp" if user.primary_goal == "both" else ("bulk" if user.primary_goal == "build_muscle" else "cut"),
        "agent_reasoning": "Fallback plan generated from profile while AI agent output is unavailable.",
    }


def _fallback_diet(user: User, workout: dict) -> dict:
    weight = float(user.weight_kg)
    tdee = int(round(weight * 33))
    strategy = workout.get("primary_strategy", "recomp")
    adjustment = 250 if strategy == "bulk" else (-350 if strategy == "cut" else 0)
    calories = max(1400, tdee + adjustment)
    protein = int(round(weight * 2.2))
    fats = int(round(weight * 0.8))
    carbs = max(80, int(round((calories - (protein * 4 + fats * 9)) / 4)))
    return {
        "tdee": float(tdee),
        "daily_calories": int(calories),
        "caloric_strategy": strategy,
        "caloric_adjustment": int(adjustment),
        "protein_g": protein,
        "carbs_g": carbs,
        "fats_g": fats,
        "meals_per_day": 3,
        "meal_complexity": "simple",
        "water_intake_liters": 3.0,
        "cheat_meals_per_week": 1,
        "dietary_preference": user.dietary_preference or "none",
        "foods_to_avoid": user.foods_to_avoid or "",
        "diet_reasoning": "Fallback nutrition targets generated from body weight and strategy.",
    }


def _fallback_timeline(user: User, workout: dict, consistency: float | None) -> dict:
    gain_needed = float(workout.get("muscle_gain_required_kg") or 0.0)
    base_months = max(4, int(round(gain_needed / 0.5))) if gain_needed > 0 else 6
    cscore = consistency if consistency is not None else 0.65
    cscore = max(0.1, min(1.0, float(cscore)))
    realistic = int(round(base_months / cscore))
    optimistic = max(3, int(round(realistic * 0.8)))
    conservative = int(round(realistic * 1.2))
    return {
        "total_months_optimistic": optimistic,
        "total_months_realistic": realistic,
        "total_months_conservative": conservative,
        "confidence_level": "medium",
        "consistency_score": cscore,
        "consistency_impact": "Higher adherence can materially shorten the timeline.",
        "phase_1_goal": "Foundation and adherence",
        "phase_1_months": max(1, realistic // 3),
        "phase_2_goal": "Primary transformation phase",
        "phase_2_months": max(2, realistic // 2),
        "phase_3_goal": "Refinement and maintenance",
        "phase_3_months": max(1, realistic - (max(1, realistic // 3) + max(2, realistic // 2))),
        "milestone_1_month": max(1, realistic // 4),
        "milestone_1_description": "Noticeable body composition improvement",
        "milestone_2_month": max(2, realistic // 2),
        "milestone_2_description": "Clear visual and strength improvements",
        "milestone_3_month": max(3, int(round(realistic * 0.85))),
        "milestone_3_description": "Near-target physique with consistent habits",
    }


@router.get("")
def get_plan(
    token: Optional[str] = None,
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
    db: Session = Depends(get_db),
):
    """Fetch current workout/diet/timeline plan."""
    user_id = get_current_user_id(token, authorization)

    transformation = db.query(TransformationPlan).filter(
        TransformationPlan.user_id == user_id
    ).order_by(TransformationPlan.created_at.desc()).first()

    timeline = db.query(Timeline).filter(
        Timeline.user_id == user_id
    ).order_by(Timeline.created_at.desc()).first()

    diet = db.query(DietaryPlan).filter(
        DietaryPlan.user_id == user_id
    ).order_by(DietaryPlan.created_at.desc()).first()

    if not transformation and not timeline and not diet:
        raise HTTPException(status_code=404, detail="No plan found for this user")

    return {
        "user_id": user_id,
        "transformation_plan": transformation,
        "timeline": timeline,
        "dietary_plan": diet,
    }


@router.post("/regenerate")
def regenerate_plan(
    token: Optional[str] = None,
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
    db: Session = Depends(get_db),
):
    """Regenerate personalized plan from latest analysis/profile."""
    user_id = get_current_user_id(token, authorization)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    latest_analysis = (
        db.query(BodyAnalysis)
        .filter(BodyAnalysis.user_id == user_id)
        .order_by(BodyAnalysis.created_at.desc())
        .first()
    )

    user_dict = _build_user_dict(user)
    analysis_dict = _analysis_from_profile(user, latest_analysis)

    gemini_key = (settings.GEMINI_API_KEY or "").strip()
    use_agents = bool(gemini_key) and not gemini_key.lower().startswith("dummy")

    if use_agents:
        try:
            workout_data = run_workout_agent(user_dict, analysis_dict)
        except Exception:
            workout_data = _fallback_workout(user, analysis_dict)

        try:
            diet_data = run_diet_agent(user_dict, analysis_dict)
        except Exception:
            diet_data = _fallback_diet(user, workout_data)

        try:
            timeline_data = run_timeline_agent(user_dict, workout_data, diet_data)
        except Exception:
            timeline_data = _fallback_timeline(user, workout_data, user.consistency_score)
    else:
        workout_data = _fallback_workout(user, analysis_dict)
        diet_data = _fallback_diet(user, workout_data)
        timeline_data = _fallback_timeline(user, workout_data, user.consistency_score)

    transformation_plan = save_transformation_plan(
        db, user_id, {k: v for k, v in workout_data.items() if k in _WORKOUT_KEYS}
    )
    dietary_plan = save_dietary_plan(
        db, user_id, {k: v for k, v in diet_data.items() if k in _DIET_KEYS}
    )
    timeline = save_timeline(
        db, user_id, {k: v for k, v in timeline_data.items() if k in _TIMELINE_KEYS}
    )

    return {
        "message": "Plan regenerated successfully",
        "user_id": user_id,
        "transformation_plan_id": transformation_plan.id,
        "dietary_plan_id": dietary_plan.id,
        "timeline_id": timeline.id,
    }
