from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import verify_jwt_token, resolve_token
from app.services.progress_service import (
    Progress,
    save_progress_entry,
    get_progress_history,
    compute_progress_metrics,
)

router = APIRouter(prefix="/progress", tags=["progress"])


class ProgressSubmit(BaseModel):
    weight_kg: Optional[float] = None
    body_fat_pct: Optional[float] = None
    notes: Optional[str] = None


def get_current_user_id(token: Optional[str], authorization: Optional[str]) -> int:
    jwt_token = resolve_token(token, authorization)
    user_id = verify_jwt_token(jwt_token) if jwt_token else None
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return int(user_id)


@router.post("")
def submit_progress(
    data: ProgressSubmit,
    token: Optional[str] = None,
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
    db: Session = Depends(get_db),
):
    """Submit a biweekly progress update."""
    user_id = get_current_user_id(token, authorization)
    entry = save_progress_entry(db, user_id, data.weight_kg, data.body_fat_pct, data.notes)
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
def get_history(
    token: Optional[str] = None,
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
    db: Session = Depends(get_db),
):
    """Get full progress history."""
    user_id = get_current_user_id(token, authorization)
    entries = get_progress_history(db, user_id)
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


@router.get("/metrics")
def get_metrics(
    token: Optional[str] = None,
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
    db: Session = Depends(get_db),
):
    """Get computed progress metrics (trends, deltas, on-track status)."""
    user_id = get_current_user_id(token, authorization)
    entries = get_progress_history(db, user_id)
    return compute_progress_metrics(entries)
