from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db, Base
from app.core.security import verify_jwt_token

router = APIRouter(prefix="/progress", tags=["progress"])


# Progress model
class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    weight_kg = Column(Float, nullable=True)
    body_fat_pct = Column(Float, nullable=True)
    lean_mass_kg = Column(Float, nullable=True)
    notes = Column(String, nullable=True)
    submitted_at = Column(DateTime, default=func.now())


class ProgressSubmit(BaseModel):
    weight_kg: Optional[float] = None
    body_fat_pct: Optional[float] = None
    notes: Optional[str] = None


def get_current_user_id(token: str) -> int:
    user_id = verify_jwt_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return int(user_id)


@router.post("")
def submit_progress(data: ProgressSubmit, token: str, db: Session = Depends(get_db)):
    """Submit biweekly progress update."""
    user_id = get_current_user_id(token)

    lean_mass = None
    if data.weight_kg and data.body_fat_pct:
        lean_mass = round(data.weight_kg * (1 - data.body_fat_pct / 100), 2)

    entry = Progress(
        user_id=user_id,
        weight_kg=data.weight_kg,
        body_fat_pct=data.body_fat_pct,
        lean_mass_kg=lean_mass,
        notes=data.notes,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    return {
        "id": entry.id,
        "user_id": entry.user_id,
        "weight_kg": entry.weight_kg,
        "body_fat_pct": entry.body_fat_pct,
        "lean_mass_kg": entry.lean_mass_kg,
        "notes": entry.notes,
        "submitted_at": entry.submitted_at,
    }


@router.get("/history")
def get_progress_history(token: str, db: Session = Depends(get_db)):
    """Get progress history."""
    user_id = get_current_user_id(token)

    entries = (
        db.query(Progress)
        .filter(Progress.user_id == user_id)
        .order_by(Progress.submitted_at.asc())
        .all()
    )

    return [
        {
            "id": e.id,
            "weight_kg": e.weight_kg,
            "body_fat_pct": e.body_fat_pct,
            "lean_mass_kg": e.lean_mass_kg,
            "notes": e.notes,
            "submitted_at": e.submitted_at,
        }
        for e in entries
    ]