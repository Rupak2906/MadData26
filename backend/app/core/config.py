from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    GEMINI_API_KEY: str
    JWT_SECRET: str
    DATABASE_URL: str
    JWT_EXPIRATION_SECONDS: int = 3600

    class Config:
        env_file = Path(__file__).resolve().parent.parent.parent / ".env"

settings = Settings()