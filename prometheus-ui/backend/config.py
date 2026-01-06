"""
Configuration management for Prometheus RAG
"""
import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging early
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


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
    OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "120"))
    
    # Redis (optional caching)
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
    REDIS_ENABLED = os.getenv("REDIS_ENABLED", "false").lower() == "true"
    REDIS_TTL = int(os.getenv("REDIS_TTL", "3600"))
    
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
    
    # Email (optional)
    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587")) if os.getenv("SMTP_PORT") else 587
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "noreply@prometheus.ai")
    
    # Analytics
    ANALYTICS_RETENTION_DAYS = int(os.getenv("ANALYTICS_RETENTION_DAYS", "90"))
    
    # Performance
    MAX_RESULTS_LIMIT = int(os.getenv("MAX_RESULTS_LIMIT", "100"))
    CHROMA_BATCH_SIZE = int(os.getenv("CHROMA_BATCH_SIZE", "10"))
    
    # Translation
    TRANSLATION_CACHE_ENABLED = os.getenv("TRANSLATION_CACHE_ENABLED", "true").lower() == "true"
    TRANSLATION_CACHE_FILE = os.getenv("TRANSLATION_CACHE_FILE", "translation_cache.json")
    
    # Query expansion
    QUERY_EXPANSION_ENABLED = os.getenv("QUERY_EXPANSION_ENABLED", "true").lower() == "true"
    
    # Reranker
    RERANKER_MODEL = os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
    
    @classmethod
    def validate(cls):
        """Validate critical configuration"""
        errors = []
        warnings = []
        
        # Critical validations
        if cls.SECRET_KEY == "change-this-in-production" and not cls.DEBUG:
            errors.append("SECRET_KEY must be set in production!")
        
        if len(cls.SECRET_KEY) < 32 and not cls.DEBUG:
            warnings.append("SECRET_KEY should be at least 32 characters for security")
        
        if cls.PORT < 1 or cls.PORT > 65535:
            errors.append(f"PORT {cls.PORT} is invalid (must be 1-65535)")
        
        if cls.SESSION_EXPIRY_DAYS < 1:
            errors.append("SESSION_EXPIRY_DAYS must be at least 1")
        
        # Log warnings
        for warning in warnings:
            logger.warning(f"⚠️  {warning}")
        
        # Raise errors
        if errors:
            logger.error("Configuration validation failed:")
            for error in errors:
                logger.error(f"❌ {error}")
            raise ValueError("Invalid configuration. Please check errors above.")
        
        logger.info("✅ Configuration validated successfully")
        return True
    
    @classmethod
    def print_summary(cls):
        """Print configuration summary"""
        logger.info("=" * 60)
        logger.info("Prometheus Configuration Summary")
        logger.info("=" * 60)
        logger.info(f"Debug Mode: {cls.DEBUG}")
        logger.info(f"Server: {cls.HOST}:{cls.PORT}")
        logger.info(f"Database: {cls.DATABASE_PATH}")
        logger.info(f"ChromaDB: {cls.CHROMA_PATH}")
        logger.info(f"Ollama: {cls.OLLAMA_BASE_URL} ({cls.OLLAMA_MODEL})")
        logger.info(f"Redis Caching: {'Enabled' if cls.REDIS_ENABLED else 'Disabled'}")
        logger.info(f"Rate Limiting: {'Enabled' if cls.RATE_LIMIT_ENABLED else 'Disabled'}")
        logger.info(f"Log Level: {cls.LOG_LEVEL}")
        logger.info("=" * 60)


# Run validation on import (but allow override for testing)
if os.getenv("SKIP_CONFIG_VALIDATION", "false").lower() != "true":
    try:
        Config.validate()
    except ValueError as e:
        logger.error(f"Configuration validation failed: {e}")
        if not Config.DEBUG:
            sys.exit(1)
