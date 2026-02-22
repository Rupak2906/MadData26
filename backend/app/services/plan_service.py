from sqlalchemy.orm import Session
from app.models.transformation_plan import TransformationPlan
from app.models.timeline import Timeline
from app.models.dietary_plan import DietaryPlan

# ── Transformation Plan ──────────────────────────────
def save_transformation_plan(db: Session, user_id: int, plan_data: dict) -> TransformationPlan:
    db_plan = TransformationPlan(user_id=user_id, **plan_data)
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan

def get_transformation_plan(db: Session, user_id: int) -> TransformationPlan:
    return db.query(TransformationPlan).filter(
        TransformationPlan.user_id == user_id
    ).order_by(TransformationPlan.created_at.desc()).first()

# ── Timeline ─────────────────────────────────────────
def save_timeline(db: Session, user_id: int, timeline_data: dict) -> Timeline:
    db_timeline = Timeline(user_id=user_id, **timeline_data)
    db.add(db_timeline)
    db.commit()
    db.refresh(db_timeline)
    return db_timeline

def get_timeline(db: Session, user_id: int) -> Timeline:
    return db.query(Timeline).filter(
        Timeline.user_id == user_id
    ).order_by(Timeline.created_at.desc()).first()

# ── Dietary Plan ─────────────────────────────────────
def save_dietary_plan(db: Session, user_id: int, diet_data: dict) -> DietaryPlan:
    db_diet = DietaryPlan(user_id=user_id, **diet_data)
    db.add(db_diet)
    db.commit()
    db.refresh(db_diet)
    return db_diet

def get_dietary_plan(db: Session, user_id: int) -> DietaryPlan:
    return db.query(DietaryPlan).filter(
        DietaryPlan.user_id == user_id
    ).order_by(DietaryPlan.created_at.desc()).first()

# ── Full Plan (everything in one call) ───────────────
def get_full_plan(db: Session, user_id: int) -> dict:
    return {
        "user_id": user_id,
        "transformation_plan": get_transformation_plan(db, user_id),
        "timeline": get_timeline(db, user_id),
        "dietary_plan": get_dietary_plan(db, user_id)
    }
