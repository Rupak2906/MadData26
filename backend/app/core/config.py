from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[3]
BACKEND_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DB_URL = f"sqlite:///{BACKEND_DIR / 'physique.db'}"

class Settings(BaseSettings):
    GEMINI_API_KEY: str = ""
    JWT_SECRET: str = "dev_jwt_secret_change_me_32_chars_min"
    DATABASE_URL: str = DEFAULT_DB_URL
    JWT_EXPIRATION_SECONDS: int = 3600

    model_config = SettingsConfigDict(
        env_file=(ROOT_DIR / ".env", BACKEND_DIR / ".env"),
        extra="ignore",
    )

settings = Settings()
