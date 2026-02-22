from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
def register():
    """Register a new user account."""
    pass

@router.post("/login")
def login():
    """User login endpoint."""
    pass

@router.get("/me")
def get_me():
    """Get current authenticated user info."""
    pass