import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "OrthoSense SaaS API"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:password@localhost:5432/orthosense"
    )
    
    # LLM
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()