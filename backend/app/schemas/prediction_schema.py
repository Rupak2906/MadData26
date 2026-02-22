from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BodyAnalysisResponse(BaseModel):
    id: int
    user_id: int
    image_path: Optional[str] = None
    shoulder_width_cm: Optional[float] = None
    hip_width_cm: Optional[float] = None
    shoulder_hip_ratio: Optional[float] = None
    chest_to_waist_ratio: Optional[float] = None
    symmetry_score: Optional[float] = None
    frame_type: Optional[str] = None
    composition_state: Optional[str] = None
    body_profile: Optional[str] = None
    body_fat_pct: Optional[float] = None
    lean_mass_kg: Optional[float] = None
    ffmi: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True
