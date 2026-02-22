from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ANTHROPIC_API_KEY: str
    JWT_SECRET: str
    DATABASE_URL: str

    class Config:
        env_file = ".env"

settings = Settings()