# Starts FastAPI app, registers routes, middleware, and initializes services.

from fastapi import FastAPI
from app.api.v1.auth_routes import router as auth_router
from app.api.v1.user_routes import router as user_router
from app.api.v1.prediction_routes import router as prediction_router
from app.api.v1.plan_routes import router as plan_router
from app.api.v1.progress_routes import router as progress_router
from app.api.v1 import plan_routes, prediction_routes
from app.api.v1.dev_routes import router as dev_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Ideal Body AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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



app = FastAPI()



# Register main routers
app.include_router(plan_routes.router)
app.include_router(prediction_routes.router)
app.include_router(dev_router)