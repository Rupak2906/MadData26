from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user_schema import UserCreate

def calculate_consistency_score(user: UserCreate) -> float:
    skip_map   = {"never": 1.0, "rarely": 0.8, "sometimes": 0.5, "often": 0.3}
    sleep_map  = {"8hr+": 1.0, "7-8hr": 0.85, "6-7hr": 0.65, "<6hr": 0.4}
    stress_map = {"low": 1.0, "moderate": 0.75, "high": 0.5}
    diet_map   = {"very_clean": 1.0, "good": 0.8, "average": 0.6, "poor": 0.35}

    skip  = skip_map.get(user.skip_frequency, 0.5)
    sleep = sleep_map.get(user.sleep_hours, 0.75)
    stress = stress_map.get(user.stress_level, 0.75)
    diet  = diet_map.get(user.diet_quality, 0.6)

    score = (skip * 0.40) + (sleep * 0.25) + (stress * 0.20) + (diet * 0.15)
    return round(score, 2)

def create_user(db: Session, user_data: UserCreate) -> User:
    consistency_score = calculate_consistency_score(user_data)
    db_user = User(
        **user_data.model_dump(),
        consistency_score=consistency_score
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int) -> User:
    return db.query(User).filter(User.id == user_id).first()

def get_all_users(db: Session) -> list:
    return db.query(User).all()

def delete_user(db: Session, user_id: int) -> bool:
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return True
    return False
