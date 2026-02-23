from fastapi import FastAPI
from app.main import app as fastapi_app

# Vercel requires the app instance to be named `app`
app = fastapi_app
