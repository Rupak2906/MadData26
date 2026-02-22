from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_jwt_token
from app.models.transformation_plan import TransformationPlan
from app.models.timeline import Timeline
from app.models.dietary_plan import DietaryPlan

router = APIRouter(prefix="/plan", tags=["plan"])


def get_current_user_id(token: str) -> int:
    user_id = verify_jwt_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return int(user_id)


@router.get("")
def get_plan(token: str, db: Session = Depends(get_db)):
    """Fetch current workout/diet/timeline plan."""
    user_id = get_current_user_id(token)

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
def regenerate_plan(token: str, db: Session = Depends(get_db)):
    """Regenerate personalized plan — triggers agent pipeline."""
    user_id = get_current_user_id(token)
    # This will be implemented by the ML team
    return {"message": "Plan regeneration queued", "user_id": user_id}