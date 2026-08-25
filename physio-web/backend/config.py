import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env file
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    load_dotenv(env_file)

class Settings:
    """Configuration settings for FastAPI application"""
    
    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    
    # Server
    PORT = int(os.getenv("PORT", 8000))
    HOST = os.getenv("HOST", "localhost")
    
    # Database
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite:///./physio_monitoring.db"
    )
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    # Security
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "your-secret-key-here-change-in-production-please"
    )
    
    # JWT
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    
    # CORS
    CORS_ORIGINS = [origin.strip() for origin in os.getenv(
        "CORS_ORIGINS",
        "*"
    ).split(",") if origin.strip()]
    if "*" not in CORS_ORIGINS:
        CORS_ORIGINS.append("*")
    
    # ML Models
    ML_MODEL_PATH = os.getenv("ML_MODEL_PATH", "./ml_models")
    ENABLE_ADVANCED_ML = os.getenv("ENABLE_ADVANCED_ML", "true").lower() == "true"
    
    # Voice
    TTS_SERVICE = os.getenv("TTS_SERVICE", "pyttsx3")
    ENABLE_VOICE = os.getenv("ENABLE_VOICE", "true").lower() == "true"
    
    # Optional
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "info")
    
    @classmethod
    def get_cors_origins(cls):
        """Get CORS origins as list"""
        return cls.CORS_ORIGINS
    
    @classmethod
    def is_production(cls):
        """Check if running in production"""
        return cls.ENVIRONMENT == "production"
    
    @classmethod
    def is_development(cls):
        """Check if running in development"""
        return cls.ENVIRONMENT == "development"


settings = Settings()
