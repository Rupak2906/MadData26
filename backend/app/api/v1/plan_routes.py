from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_jwt_token
from app.models.user import User
from app.models.transformation_plan import TransformationPlan
from app.models.timeline import Timeline
from app.models.dietary_plan import DietaryPlan
from app.services.prediction_service import get_body_analysis
from app.services.planner_service import generate_and_save_plan

router = APIRouter(prefix="/plan", tags=["plan"])


def get_current_user(token: str, db: Session) -> User:
    user_id = verify_jwt_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("")
def get_plan(token: str, db: Session = Depends(get_db)):
    """Fetch the most recent workout/diet/timeline plan for the current user."""
    user = get_current_user(token, db)

    transformation = db.query(TransformationPlan).filter(
        TransformationPlan.user_id == user.id
    ).order_by(TransformationPlan.created_at.desc()).first()

    timeline = db.query(Timeline).filter(
        Timeline.user_id == user.id
    ).order_by(Timeline.created_at.desc()).first()

    diet = db.query(DietaryPlan).filter(
        DietaryPlan.user_id == user.id
    ).order_by(DietaryPlan.created_at.desc()).first()

    if not transformation and not timeline and not diet:
        raise HTTPException(status_code=404, detail="No plan found. Please complete a body scan first.")

    return {
        "user_id": user.id,
        "transformation_plan": transformation,
        "timeline": timeline,
        "dietary_plan": diet,
    }


@router.post("/regenerate")
def regenerate_plan(token: str, db: Session = Depends(get_db)):
    """
    Regenerate the full plan using the last saved body analysis.
    Re-runs all three Claude/Gemini agents without requiring new images.
    """
    user = get_current_user(token, db)

    # Fetch last body analysis from DB
    last_analysis = get_body_analysis(db, user.id)
    if not last_analysis:
        raise HTTPException(
            status_code=404,
            detail="No body scan found. Please complete a scan first via POST /predict."
        )

    user_dict = {
        "name": user.name,
        "age": user.age,
        "biological_sex": user.biological_sex,
        "height_cm": user.height_cm,
        "weight_kg": user.weight_kg,
        "experience_level": user.experience_level,
        "days_available": user.days_available,
        "primary_goal": user.primary_goal,
        "diet_strictness": user.diet_strictness,
        "consistency_score": user.consistency_score,
        "dietary_preference": user.dietary_preference,
        "foods_to_avoid": user.foods_to_avoid,
        "sleep_hours": user.sleep_hours,
        "stress_level": user.stress_level,
        "job_activity": user.job_activity,
        "diet_quality": user.diet_quality,
        "skip_frequency": user.skip_frequency,
        "meals_per_day": user.meals_per_day,
        "uses_supplements": user.uses_supplements,
        "session_duration": user.session_duration,
        "follows_progressive_overload": user.follows_progressive_overload,
    }

    analysis_dict = {
        "frame_type": last_analysis.frame_type,
        "body_fat_pct": last_analysis.body_fat_pct,
        "lean_mass_kg": last_analysis.lean_mass_kg,
        "ffmi": last_analysis.ffmi,
        "shoulder_hip_ratio": last_analysis.shoulder_hip_ratio,
        "symmetry_score": last_analysis.symmetry_score,
        "shoulder_width_cm": last_analysis.shoulder_width_cm,
        "hip_width_cm": last_analysis.hip_width_cm,
        "torso_length_cm": last_analysis.torso_length_cm,
        "arm_length_cm": last_analysis.arm_length_cm,
        "leg_length_cm": last_analysis.leg_length_cm,
    }

    try:
        result = generate_and_save_plan(db, user.id, user_dict, analysis_dict)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {e}")

    return result   