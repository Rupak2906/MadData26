"""
progress_service.py
-------------------
Processes user biweekly progress submissions and computes trend metrics.
"""

from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


# ── Progress model (defined here to keep it self-contained) ───────────────────

class Progress(Base):
    __tablename__ = "progress"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    user_id      = Column(Integer, nullable=False)
    weight_kg    = Column(Float, nullable=True)
    body_fat_pct = Column(Float, nullable=True)
    lean_mass_kg = Column(Float, nullable=True)
    notes        = Column(String, nullable=True)
    submitted_at = Column(DateTime, default=func.now())


# ── Service functions ─────────────────────────────────────────────────────────

def save_progress_entry(
    db: Session,
    user_id: int,
    weight_kg: float | None,
    body_fat_pct: float | None,
    notes: str | None,
) -> Progress:
    """Save a new progress entry and compute lean mass if possible."""
    lean_mass = None
    if weight_kg is not None and body_fat_pct is not None:
        lean_mass = round(weight_kg * (1 - body_fat_pct / 100), 2)

    entry = Progress(
        user_id=user_id,
        weight_kg=weight_kg,
        body_fat_pct=body_fat_pct,
        lean_mass_kg=lean_mass,
        notes=notes,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_progress_history(db: Session, user_id: int) -> list[Progress]:
    """Return all progress entries for a user, oldest first."""
    return (
        db.query(Progress)
        .filter(Progress.user_id == user_id)
        .order_by(Progress.submitted_at.asc())
        .all()
    )


def compute_progress_metrics(entries: list[Progress]) -> dict:
    """
    Compute summary metrics from a list of progress entries.
    Returns deltas and rates of change between first and latest entry.
    """
    if len(entries) < 2:
        return {"message": "Not enough entries to compute trends. Keep logging!"}

    first = entries[0]
    latest = entries[-1]

    weight_delta = None
    lean_delta = None
    bf_delta = None

    if first.weight_kg is not None and latest.weight_kg is not None:
        weight_delta = round(latest.weight_kg - first.weight_kg, 2)

    if first.lean_mass_kg is not None and latest.lean_mass_kg is not None:
        lean_delta = round(latest.lean_mass_kg - first.lean_mass_kg, 2)

    if first.body_fat_pct is not None and latest.body_fat_pct is not None:
        bf_delta = round(latest.body_fat_pct - first.body_fat_pct, 2)

    # Estimate weeks between entries
    weeks = None
    if first.submitted_at and latest.submitted_at:
        delta_days = (latest.submitted_at - first.submitted_at).days
        weeks = max(delta_days / 7, 1)

    return {
        "total_entries": len(entries),
        "weeks_tracked": round(weeks, 1) if weeks else None,
        "weight_change_kg": weight_delta,
        "lean_mass_change_kg": lean_delta,
        "body_fat_change_pct": bf_delta,
        "lean_mass_per_week_kg": round(lean_delta / weeks, 3) if lean_delta and weeks else None,
        "on_track": lean_delta is not None and lean_delta > 0,
    }