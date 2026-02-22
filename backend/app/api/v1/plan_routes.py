from fastapi import APIRouter

router = APIRouter(prefix="/plan", tags=["plan"])

@router.get("")
def get_plan():
    """Fetch current workout/diet/timeline plan."""
    pass

@router.post("/regenerate")
def regenerate_plan():
    """Regenerate personalized plan."""
    pass