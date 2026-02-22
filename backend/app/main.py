
from fastapi import FastAPI
from app.api.v1 import plan_routes, prediction_routes
from app.api.v1.dev_routes import router as dev_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register main routers
app.include_router(plan_routes.router)
app.include_router(prediction_routes.router)
app.include_router(dev_router)