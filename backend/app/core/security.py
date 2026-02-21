# Password hashing, JWT token creation, and authentication helpers.

import hashlib
import secrets
import time
import jwt

def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def create_jwt_token(user_id: str, expiration_time: int = 3600) -> str:
    """Create a JWT token for a user."""
    payload = {
        "user_id": user_id,
        "exp": expiration_time
    }
    return jwt.encode(payload, "secret_key", algorithm="HS256")

def verify_jwt_token(token: str) -> str:
    """Verify a JWT token and return the user ID."""
    try:
        payload = jwt.decode(token, "secret_key", algorithms=["HS256"])
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None