import hashlib
import time
import jwt

SECRET_KEY = "your_secret_key_change_in_production"
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def create_jwt_token(user_id: str, expiration_time: int = None) -> str:
    """Create a JWT token for a user."""
    if expiration_time is None:
        expiration_time = int(time.time()) + 3600  # 1 hour from now
    payload = {
        "user_id": user_id,
        "exp": expiration_time,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_jwt_token(token: str) -> str:
    """Verify a JWT token and return the user ID."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None