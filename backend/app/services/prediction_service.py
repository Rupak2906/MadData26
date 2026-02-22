from sqlalchemy.orm import Session
from app.models.body_analysis import BodyAnalysis

def save_body_analysis(db: Session, user_id: int, analysis_data: dict) -> BodyAnalysis:
    db_analysis = BodyAnalysis(
        user_id=user_id,
        **analysis_data
    )
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    return db_analysis

def get_body_analysis(db: Session, user_id: int) -> BodyAnalysis:
    return db.query(BodyAnalysis).filter(
        BodyAnalysis.user_id == user_id
    ).order_by(BodyAnalysis.created_at.desc()).first()

def get_all_analyses(db: Session, user_id: int) -> list:
    return db.query(BodyAnalysis).filter(
        BodyAnalysis.user_id == user_id
    ).all()
