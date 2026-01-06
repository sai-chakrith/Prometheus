"""
Environment configuration validator for Prometheus
Ensures all required variables are set and valid before startup
"""
import os
import sys
import logging
from typing import List, Tuple, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class ConfigValidator:
    """Validates environment configuration"""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_required(self, key: str, env_value: Optional[str]) -> bool:
        """Validate that a required variable is set"""
        if not env_value:
            self.errors.append(f"Required environment variable '{key}' is not set")
            return False
        return True
    
    def validate_integer(self, key: str, env_value: Optional[str], min_val: Optional[int] = None, max_val: Optional[int] = None) -> bool:
        """Validate integer value with optional range"""
        if not env_value:
            return True  # Skip if not set
        
        try:
            value = int(env_value)
            if min_val is not None and value < min_val:
                self.errors.append(f"{key}={value} is below minimum {min_val}")
                return False
            if max_val is not None and value > max_val:
                self.errors.append(f"{key}={value} is above maximum {max_val}")
                return False
            return True
        except ValueError:
            self.errors.append(f"{key}='{env_value}' is not a valid integer")
            return False
    
    def validate_boolean(self, key: str, env_value: Optional[str]) -> bool:
        """Validate boolean value"""
        if not env_value:
            return True
        
        if env_value.lower() not in ['true', 'false', '1', '0', 'yes', 'no']:
            self.errors.append(f"{key}='{env_value}' is not a valid boolean (use: true/false)")
            return False
        return True
    
    def validate_url(self, key: str, env_value: Optional[str]) -> bool:
        """Validate URL format"""
        if not env_value:
            return True
        
        try:
            result = urlparse(env_value)
            if not all([result.scheme, result.netloc]):
                self.errors.append(f"{key}='{env_value}' is not a valid URL")
                return False
            return True
        except Exception:
            self.errors.append(f"{key}='{env_value}' is not a valid URL")
            return False
    
    def validate_file_path(self, key: str, env_value: Optional[str], must_exist: bool = False) -> bool:
        """Validate file path"""
        if not env_value:
            return True
        
        if must_exist and not os.path.exists(env_value):
            self.warnings.append(f"{key}='{env_value}' - file does not exist yet")
        return True
    
    def validate_choice(self, key: str, env_value: Optional[str], choices: List[str]) -> bool:
        """Validate value is one of allowed choices"""
        if not env_value:
            return True
        
        if env_value not in choices:
            self.errors.append(f"{key}='{env_value}' must be one of: {', '.join(choices)}")
            return False
        return True
    
    def validate_secret_key(self, key: str, env_value: Optional[str], is_production: bool) -> bool:
        """Validate secret key strength"""
        if not env_value:
            self.errors.append(f"Required environment variable '{key}' is not set")
            return False
        
        if env_value == "change-this-in-production" or env_value == "change-this-in-production-use-openssl-rand-hex-32":
            if is_production:
                self.errors.append(f"{key} must be changed from default in production!")
                return False
            else:
                self.warnings.append(f"{key} is using default value - change for production")
        
        if len(env_value) < 32:
            self.warnings.append(f"{key} should be at least 32 characters for security")
        
        return True
    
    def validate_all(self) -> Tuple[bool, List[str], List[str]]:
        """Run all validations"""
        self.errors = []
        self.warnings = []
        
        # Get environment variables
        secret_key = os.getenv("SECRET_KEY")
        debug = os.getenv("DEBUG", "false")
        is_production = debug.lower() != "true"
        
        # Security
        self.validate_secret_key("SECRET_KEY", secret_key, is_production)
        self.validate_integer("SESSION_EXPIRY_DAYS", os.getenv("SESSION_EXPIRY_DAYS"), min_val=1, max_val=365)
        
        # Database
        self.validate_file_path("DATABASE_PATH", os.getenv("DATABASE_PATH"))
        self.validate_file_path("CHROMA_PATH", os.getenv("CHROMA_PATH"))
        
        # Ollama
        self.validate_url("OLLAMA_BASE_URL", os.getenv("OLLAMA_BASE_URL"))
        ollama_model = os.getenv("OLLAMA_MODEL")
        if ollama_model and len(ollama_model.strip()) == 0:
            self.warnings.append("OLLAMA_MODEL is empty")
        
        # Redis
        redis_enabled = os.getenv("REDIS_ENABLED", "false")
        self.validate_boolean("REDIS_ENABLED", redis_enabled)
        if redis_enabled.lower() == "true":
            self.validate_integer("REDIS_PORT", os.getenv("REDIS_PORT"), min_val=1, max_val=65535)
            self.validate_integer("REDIS_TTL", os.getenv("REDIS_TTL"), min_val=1)
        
        # Server
        self.validate_integer("PORT", os.getenv("PORT"), min_val=1, max_val=65535)
        self.validate_boolean("DEBUG", debug)
        
        # Rate limiting
        self.validate_boolean("RATE_LIMIT_ENABLED", os.getenv("RATE_LIMIT_ENABLED"))
        
        # Dataset
        dataset_path = os.getenv("DATASET_PATH")
        if dataset_path:
            self.validate_file_path("DATASET_PATH", dataset_path, must_exist=True)
        
        # Whisper
        self.validate_choice(
            "WHISPER_MODEL_SIZE",
            os.getenv("WHISPER_MODEL_SIZE"),
            ["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"]
        )
        self.validate_choice(
            "WHISPER_DEVICE",
            os.getenv("WHISPER_DEVICE"),
            ["cpu", "cuda"]
        )
        self.validate_choice(
            "WHISPER_COMPUTE_TYPE",
            os.getenv("WHISPER_COMPUTE_TYPE"),
            ["int8", "float16", "float32"]
        )
        
        # Logging
        self.validate_choice(
            "LOG_LEVEL",
            os.getenv("LOG_LEVEL"),
            ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        )
        
        # Analytics
        self.validate_integer("ANALYTICS_RETENTION_DAYS", os.getenv("ANALYTICS_RETENTION_DAYS"), min_val=1)
        
        # Performance
        self.validate_integer("MAX_RESULTS_LIMIT", os.getenv("MAX_RESULTS_LIMIT"), min_val=1, max_val=1000)
        self.validate_integer("CHROMA_BATCH_SIZE", os.getenv("CHROMA_BATCH_SIZE"), min_val=1, max_val=100)
        
        # Email (if configured)
        smtp_host = os.getenv("SMTP_HOST")
        if smtp_host:
            self.validate_integer("SMTP_PORT", os.getenv("SMTP_PORT"), min_val=1, max_val=65535)
        
        # Celery (if configured)
        celery_broker = os.getenv("CELERY_BROKER_URL")
        if celery_broker:
            self.validate_url("CELERY_BROKER_URL", celery_broker)
            self.validate_url("CELERY_RESULT_BACKEND", os.getenv("CELERY_RESULT_BACKEND"))
        
        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings
    
    def print_report(self):
        """Print validation report"""
        is_valid, errors, warnings = self.validate_all()
        
        if errors:
            logger.error("=" * 60)
            logger.error("CONFIGURATION ERRORS DETECTED")
            logger.error("=" * 60)
            for error in errors:
                logger.error(f"❌ {error}")
            logger.error("=" * 60)
        
        if warnings:
            logger.warning("=" * 60)
            logger.warning("CONFIGURATION WARNINGS")
            logger.warning("=" * 60)
            for warning in warnings:
                logger.warning(f"⚠️  {warning}")
            logger.warning("=" * 60)
        
        if is_valid and not warnings:
            logger.info("✅ All configuration validations passed")
        
        return is_valid


def validate_config() -> bool:
    """Validate configuration and exit if invalid"""
    validator = ConfigValidator()
    is_valid = validator.print_report()
    
    if not is_valid:
        logger.error("Configuration validation failed. Please fix errors before starting.")
        sys.exit(1)
    
    return True


if __name__ == "__main__":
    # Run validation from command line
    validate_config()
    print("✅ Configuration is valid")
