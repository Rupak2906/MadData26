from fastapi import APIRouter

router = APIRouter(prefix="/predict", tags=["predict"])

@router.post("")
def upload_image():
    """Upload image for body analysis/prediction."""
    pass

@router.get("/{scan_id}")
def get_prediction(scan_id: str):
    """Get processing result/status for a given scan."""
    pass