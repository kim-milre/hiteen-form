from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./survey.db"
    CORS_ORIGINS: str = "http://localhost:5174"

settings = Settings()