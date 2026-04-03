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

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "0rth0$ense!_s3cr3t_v3ry_s3cur3")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))

    class Config:
        case_sensitive = True
        # Load from backend/.env if running from project root, or .env if running from backend
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")

settings = Settings()