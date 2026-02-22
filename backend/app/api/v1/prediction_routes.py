"""
prediction_routes.py
--------------------
POST /predict
  1. Decode + validate front & back images via CVService
  2. Build feature vector from CV output + user profile
  3. Run ML models (frame type, peak lean mass, timeline)
  4. Run Claude agents (diet, workout, timeline narrative)
  5. Save BodyAnalysis + all plans to DB
  6. Return full plan response

GET /predict/{scan_id}
  Returns a previously saved body analysis by ID.
"""

from fastapi import APIRouter, UploadFile, Form, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import numpy as np
import cv2
from typing import Any

from app.core.database import get_db
from app.core.security import verify_jwt_token
from app.models.user import User
from app.services.cv_service import CVService, ValidationError, RawMeasurements
from app.services.prediction_service import save_body_analysis, get_body_analysis
from app.services.plan_service import save_transformation_plan, save_timeline, save_dietary_plan
from app.agents.diet_agent import run_diet_agent
from app.agents.workout_agent import run_workout_agent
from app.agents.timeline_agent import run_timeline_agent

router = APIRouter(prefix="/predict", tags=["predict"])


# ── Auth helper ────────────────────────────────────────────────────────────────

def get_current_user(token: str, db: Session) -> User:
    user_id = verify_jwt_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ── ML inference (lazy import so server starts even without .pkl files) ────────

def run_ml_models(raw: RawMeasurements, user: User) -> dict:
    """
    Attempt to run the trained ML models.
    Falls back to formula-based estimates if models are not yet trained.
    """
    try:
        from app.ML.features import RawMeasurements as MLRaw, UserInputs, build_feature_vector
        from app.ML.inference import predict, extract_features

        ml_raw = MLRaw(
            shoulder_width_n=raw.shoulder_width_n,
            hip_width_n=raw.hip_width_n,
            waist_width_n=raw.waist_width_n,
            torso_length_n=raw.torso_length_n,
            leg_length_n=raw.leg_length_n,
            arm_length_n=raw.arm_length_n,
            upper_arm_n=raw.upper_arm_n,
            forearm_n=raw.forearm_n,
            thigh_n=raw.thigh_n,
            calf_n=raw.calf_n,
            symmetry_score=raw.symmetry_score,
        )

        intensity_map = {"beginner": 0, "intermediate": 1, "advanced": 2}
        ml_user = UserInputs(
            sex=1 if user.biological_sex == "male" else 0,
            age=float(user.age),
            height_cm=user.height_cm,
            weight_kg=user.weight_kg,
            intensity=intensity_map.get(user.experience_level, 1),
            weekly_training_days=user.days_available or 4,
        )

        fv = extract_features(ml_raw, ml_user)
        result = predict(fv)
        return result.to_dict()

    except Exception as e:
        print(f"[ML fallback] Models not available, using formulas: {e}")
        return _formula_fallback(raw, user)


def _formula_fallback(raw: RawMeasurements, user: User) -> dict:
    """Berkhan/Deurenberg formula estimates when ML models are not available."""
    height_m = user.height_cm / 100
    bmi = user.weight_kg / (height_m ** 2)
    sex = 1 if user.biological_sex == "male" else 0
    bf_pct = max(5.0, min(50.0, (1.20 * bmi) + (0.23 * user.age) - (10.8 * sex) - 5.4))
    lean_mass = user.weight_kg * (1 - bf_pct / 100)
    ffmi = lean_mass / (height_m ** 2)

    shr = raw.shoulder_width_n / (raw.hip_width_n + 1e-6)
    if shr >= 1.35:
        frame_type, frame_label, frame_bonus = "wide", 2, 1.0
    elif shr <= 1.15:
        frame_type, frame_label, frame_bonus = "narrow", 0, -1.0
    else:
        frame_type, frame_label, frame_bonus = "balanced", 1, 0.0

    base_ffmi = 24.5 if sex else 21.0
    peak_ffmi = base_ffmi + frame_bonus
    peak_lean_mass = peak_ffmi * (height_m ** 2)
    lean_gap = max(peak_lean_mass - lean_mass, 0)

    intensity_map = {"beginner": 0.90, "intermediate": 0.45, "advanced": 0.20}
    monthly_rate = intensity_map.get(user.experience_level, 0.45)
    months = round(lean_gap / monthly_rate, 1) if monthly_rate > 0 else 24.0

    return {
        "frame_type": frame_type,
        "frame_label": frame_label,
        "frame_confidence": 0.75,
        "current_lean_mass_kg": round(lean_mass, 2),
        "current_ffmi": round(ffmi, 2),
        "predicted_body_fat_pct": round(bf_pct, 1),
        "peak_lean_mass_kg": round(peak_lean_mass, 2),
        "peak_ffmi": round(peak_ffmi, 2),
        "lean_mass_gap_kg": round(lean_gap, 2),
        "months_realistic": months,
        "months_optimistic": round(months * 0.80, 1),
        "months_conservative": round(months * 1.20, 1),
    }


# ── Merge front + back measurements ───────────────────────────────────────────

def merge_measurements(front: RawMeasurements, back: RawMeasurements) -> RawMeasurements:
    """Average complementary measurements from front and back scans."""
    return RawMeasurements(
        shoulder_width_n=(front.shoulder_width_n + back.shoulder_width_n) / 2,
        hip_width_n=(front.hip_width_n + back.hip_width_n) / 2,
        waist_width_n=front.waist_width_n,
        torso_length_n=(front.torso_length_n + back.torso_length_n) / 2,
        leg_length_n=(front.leg_length_n + back.leg_length_n) / 2,
        arm_length_n=(front.arm_length_n + back.arm_length_n) / 2,
        upper_arm_n=(front.upper_arm_n + back.upper_arm_n) / 2,
        forearm_n=(front.forearm_n + back.forearm_n) / 2,
        thigh_n=(front.thigh_n + back.thigh_n) / 2,
        calf_n=(front.calf_n + back.calf_n) / 2,
        symmetry_score=(front.symmetry_score + back.symmetry_score) / 2,
    )


# ── Main scan + plan endpoint ──────────────────────────────────────────────────

@router.post("")
async def upload_and_predict(
    front_image: UploadFile,
    back_image: UploadFile,
    front_pose_type: str = Form(...),
    back_pose_type: str = Form(...),
    token: str = Form(...),
    db: Session = Depends(get_db),
) -> Any:
    """
    Full scan-to-plan pipeline.
    Accepts front + back body images, returns a complete personalised plan.
    """

    # 1. Authenticate
    user = get_current_user(token, db)

    # 2. Decode images
    async def decode(upload: UploadFile) -> np.ndarray:
        data = await upload.read()
        arr = np.frombuffer(data, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            raise HTTPException(status_code=400, detail=f"Could not decode image: {upload.filename}")
        return img

    img_front = await decode(front_image)
    img_back = await decode(back_image)

    # 3. Validate pose types
    if front_pose_type.lower() != "front" or back_pose_type.lower() != "back":
        raise HTTPException(
            status_code=400,
            detail="front_pose_type must be 'front' and back_pose_type must be 'back'"
        )

    # 4. CV validation
    cv = CVService()
    errors = []
    try:
        cv.validate_features(img_front, pose_type="front")
    except ValidationError as e:
        errors.append(f"front: {e.message}")
    try:
        cv.validate_features(img_back, pose_type="back")
    except ValidationError as e:
        errors.append(f"back: {e.message}")

    if errors:
        return JSONResponse(status_code=400, content={"status": "rejected", "details": errors})

    # 5. Extract measurements
    try:
        raw_front = cv.process_image(img_front, "front")
        raw_back = cv.process_image(img_back, "back")
    except ValidationError as e:
        return JSONResponse(
            status_code=400,
            content={"status": e.status, "reason": e.reason, "message": e.message}
        )

    raw = merge_measurements(raw_front, raw_back)

    # 6. ML prediction
    ml = run_ml_models(raw, user)

    # 7. Save body analysis
    body_analysis_data = {
        "shoulder_width_cm": round(raw.shoulder_width_n * user.height_cm, 2),
        "hip_width_cm": round(raw.hip_width_n * user.height_cm, 2),
        "torso_length_cm": round(raw.torso_length_n * user.height_cm, 2),
        "arm_length_cm": round(raw.arm_length_n * user.height_cm, 2),
        "leg_length_cm": round(raw.leg_length_n * user.height_cm, 2),
        "shoulder_hip_ratio": round(raw.shoulder_width_n / (raw.hip_width_n + 1e-6), 3),
        "symmetry_score": round(raw.symmetry_score, 3),
        "frame_type": ml["frame_type"],
        "body_fat_pct": ml["predicted_body_fat_pct"],
        "lean_mass_kg": ml["current_lean_mass_kg"],
        "ffmi": ml["current_ffmi"],
    }
    body_analysis = save_body_analysis(db, user.id, body_analysis_data)

    # 8. Build agent context
    user_dict = {
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

    analysis_dict = {
        **body_analysis_data,
        "peak_lean_mass_kg": ml["peak_lean_mass_kg"],
        "peak_ffmi": ml["peak_ffmi"],
        "lean_mass_gap_kg": ml["lean_mass_gap_kg"],
        "months_realistic": ml["months_realistic"],
    }

    # 9. Run Claude agents
    _WORKOUT_KEYS = [
        "peak_lean_mass_kg", "target_bf_pct", "peak_ffmi",
        "muscle_gain_required_kg", "fat_loss_required_pct",
        "muscle_gaps", "primary_strategy", "agent_reasoning"
    ]
    _DIET_KEYS = [
        "tdee", "daily_calories", "caloric_strategy", "caloric_adjustment",
        "protein_g", "carbs_g", "fats_g", "meals_per_day", "meal_complexity",
        "water_intake_liters", "cheat_meals_per_week", "dietary_preference",
        "foods_to_avoid", "diet_reasoning"
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

    try:
        workout_data = run_workout_agent(user_dict, analysis_dict)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Workout agent error: {e}")

    try:
        diet_data = run_diet_agent(user_dict, analysis_dict)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Diet agent error: {e}")

    try:
        timeline_data = run_timeline_agent(user_dict, workout_data, diet_data)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Timeline agent error: {e}")

    # 10. Save plans
    transformation_plan = save_transformation_plan(
        db, user.id, {k: v for k, v in workout_data.items() if k in _WORKOUT_KEYS}
    )
    dietary_plan = save_dietary_plan(
        db, user.id, {k: v for k, v in diet_data.items() if k in _DIET_KEYS}
    )
    timeline = save_timeline(
        db, user.id, {k: v for k, v in timeline_data.items() if k in _TIMELINE_KEYS}
    )

    return {
        "user_id": user.id,
        "body_analysis": {"id": body_analysis.id, **body_analysis_data, **{k: ml[k] for k in ["peak_lean_mass_kg", "peak_ffmi", "lean_mass_gap_kg"]}},
        "transformation_plan": {"id": transformation_plan.id, **workout_data},
        "dietary_plan": {"id": dietary_plan.id, **diet_data},
        "timeline": {"id": timeline.id, **timeline_data},
    }


@router.get("/{scan_id}")
def get_prediction(scan_id: int, token: str, db: Session = Depends(get_db)):
    """Retrieve a saved body analysis by ID."""
    user_id = verify_jwt_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    analysis = db.query(__import__("app.models.body_analysis", fromlist=["BodyAnalysis"]).BodyAnalysis).filter_by(id=scan_id, user_id=int(user_id)).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Scan not found")
    return analysis