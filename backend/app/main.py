from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.models import User, BodyAnalysis, TransformationPlan, Timeline, DietaryPlan
from app.api.v1 import auth_routes

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Physique Predictor",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)

@app.get("/")
def root():
    return {"status": "running", "message": "AI Physique Predictor API"}

@app.get("/health")
def health():
    return {"status": "healthy"}
