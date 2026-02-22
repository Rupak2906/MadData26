# Starts FastAPI app, registers routes, middleware, and initializes services.

from fastapi import FastAPI
from app.api.v1.auth_routes import router as auth_router
from app.api.v1.user_routes import router as user_router
from app.api.v1.prediction_routes import router as prediction_router
from app.api.v1.plan_routes import router as plan_router
from app.api.v1.progress_routes import router as progress_router

app = FastAPI(title="Ideal Body AI")

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(prediction_router)
app.include_router(plan_router)
app.include_router(progress_router)

@app.get("/")
def root():
    return {"message": "Welcome to Ideal Body AI!"}

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return {}