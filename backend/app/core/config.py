from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Journex"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    
    # Database settings
    DATABASE_URL: Optional[str] = None
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: str = "5432"
    DATABASE_NAME: str = "journex_db"
    DATABASE_USER: str = "journex_user"
    DATABASE_PASSWORD: str = "journex_password"
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # This allows extra fields in .env

settings = Settings()
