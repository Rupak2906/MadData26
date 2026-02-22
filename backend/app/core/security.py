import bcrypt
import time
import jwt
from app.core.config import settings


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a bcrypt-hashed password."""
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_jwt_token(user_id: str, expiration_time: int = None) -> str:
    """Create a JWT token for a user."""
    if expiration_time is None:
        expiration_time = int(time.time()) + settings.JWT_EXPIRATION_SECONDS
    payload = {
        "user_id": user_id,
        "exp": expiration_time,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


def verify_jwt_token(token: str) -> str | None:
    """Verify a JWT token and return the user ID, or None if invalid."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None