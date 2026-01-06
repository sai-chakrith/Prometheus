"""
Configuration management for Prometheus RAG
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production")
    SESSION_EXPIRY_DAYS = int(os.getenv("SESSION_EXPIRY_DAYS", "30"))
    
    # Database
    DATABASE_PATH = os.getenv("DATABASE_PATH", "prometheus.db")
    CHROMA_PATH = os.getenv("CHROMA_PATH", "chroma_db")
    
    # Ollama
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    
    # Redis (optional caching)
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_ENABLED = os.getenv("REDIS_ENABLED", "false").lower() == "true"
    
    # CORS
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
    
    # Server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    # Rate Limiting
    RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    LOGIN_RATE_LIMIT = os.getenv("LOGIN_RATE_LIMIT", "5/minute")
    API_RATE_LIMIT = os.getenv("API_RATE_LIMIT", "100/minute")
    
    # Dataset
    DATASET_PATH = os.getenv("DATASET_PATH", "../../dataset/cleaned_funding_synthetic_2010_2025.csv")
    
    # Whisper STT
    WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "large-v3")
    WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cpu")
    WHISPER_COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE_TYPE", "int8")
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls):
        """Validate critical configuration"""
        if cls.SECRET_KEY == "change-this-in-production" and not cls.DEBUG:
            raise ValueError("SECRET_KEY must be set in production!")
        return True

# Validate config on import
Config.validate()
