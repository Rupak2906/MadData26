# Endpoints for user profile management (GET/PATCH profile).

from fastapi import APIRouter

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/profile")
def get_profile():
    """Get user profile (height, weight, goals, etc.)"""
    pass

@router.patch("/profile")
def update_profile():
    """Update user profile."""
    pass
