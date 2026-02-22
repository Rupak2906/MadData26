# Starts FastAPI app, registers routes, middleware, and initializes services.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.auth_routes import router as auth_router
from app.api.v1.user_routes import router as user_router
from app.api.v1.prediction_routes import router as prediction_router
from app.api.v1.plan_routes import router as plan_router
from app.api.v1.progress_routes import router as progress_router
from app.api.v1.dev_routes import router as dev_router

app = FastAPI(title="Ideal Body AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router,       prefix="/api/v1")
app.include_router(user_router,       prefix="/api/v1")
app.include_router(prediction_router, prefix="/api/v1")
app.include_router(plan_router,       prefix="/api/v1")
app.include_router(progress_router,   prefix="/api/v1")
app.include_router(dev_router,        prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Welcome to Ideal Body AI!"}

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return {}