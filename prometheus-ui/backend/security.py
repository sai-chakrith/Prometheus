"""
Enhanced security utilities for Prometheus
Includes CSRF protection, secure headers, and security middleware
"""
import secrets
import hashlib
import logging
from typing import Optional, Callable
from fastapi import Request, HTTPException, status
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.datastructures import Headers

logger = logging.getLogger(__name__)


class CSRFProtection:
    """CSRF token generation and validation"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
    
    def generate_token(self, session_id: str) -> str:
        """Generate CSRF token for session"""
        # Generate random token
        random_token = secrets.token_urlsafe(32)
        
        # Create signature
        message = f"{session_id}:{random_token}".encode()
        signature = hashlib.sha256(
            message + self.secret_key.encode()
        ).hexdigest()
        
        # Combine token and signature
        csrf_token = f"{random_token}.{signature}"
        return csrf_token
    
    def validate_token(self, token: str, session_id: str) -> bool:
        """Validate CSRF token"""
        if not token or not session_id:
            return False
        
        try:
            # Split token and signature
            parts = token.split('.')
            if len(parts) != 2:
                return False
            
            random_token, provided_signature = parts
            
            # Recreate signature
            message = f"{session_id}:{random_token}".encode()
            expected_signature = hashlib.sha256(
                message + self.secret_key.encode()
            ).hexdigest()
            
            # Compare signatures
            return secrets.compare_digest(provided_signature, expected_signature)
            
        except Exception as e:
            logger.warning(f"CSRF validation error: {e}")
            return False


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' http://localhost:* ws://localhost:*; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp
        
        # Permissions Policy (formerly Feature-Policy)
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "accelerometer=()"
        )
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests for security auditing"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Log request
        client_ip = request.client.host if request.client else "unknown"
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {client_ip}"
        )
        
        # Process request
        response = await call_next(request)
        
        # Log response
        logger.info(
            f"Response: {request.method} {request.url.path} "
            f"status={response.status_code}"
        )
        
        return response


class RateLimitExceededError(HTTPException):
    """Custom exception for rate limit exceeded"""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )


def validate_csrf_token(request: Request, csrf_protection: CSRFProtection):
    """
    Dependency to validate CSRF token on protected endpoints
    
    Usage:
        @app.post("/protected-endpoint")
        async def endpoint(request: Request):
            validate_csrf_token(request, csrf_protection)
            # ... rest of endpoint logic
    """
    # Get session ID from header
    session_id = request.headers.get("X-Session-Id")
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session ID required"
        )
    
    # Get CSRF token from header
    csrf_token = request.headers.get("X-CSRF-Token")
    if not csrf_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token required"
        )
    
    # Validate token
    if not csrf_protection.validate_token(csrf_token, session_id):
        logger.warning(f"Invalid CSRF token for session {session_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid CSRF token"
        )


def sanitize_input(text: str, max_length: int = 10000) -> str:
    """
    Sanitize user input to prevent injection attacks
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
    
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Truncate to max length
    text = text[:max_length]
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def generate_secure_token(length: int = 32) -> str:
    """Generate cryptographically secure random token"""
    return secrets.token_urlsafe(length)


def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """
    Hash password with salt using bcrypt-like approach
    
    Args:
        password: Plain text password
        salt: Optional salt (generated if not provided)
    
    Returns:
        Tuple of (hashed_password, salt)
    """
    import bcrypt
    
    if salt is None:
        salt = bcrypt.gensalt()
    elif isinstance(salt, str):
        salt = salt.encode()
    
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode(), salt.decode()


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify password against hash
    
    Args:
        password: Plain text password to verify
        hashed_password: Hashed password to check against
    
    Returns:
        True if password matches, False otherwise
    """
    import bcrypt
    
    try:
        return bcrypt.checkpw(
            password.encode(),
            hashed_password.encode()
        )
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


def is_strong_password(password: str) -> tuple[bool, list[str]]:
    """
    Check if password meets strength requirements
    
    Args:
        password: Password to check
    
    Returns:
        Tuple of (is_strong, list_of_issues)
    """
    issues = []
    
    if len(password) < 8:
        issues.append("Password must be at least 8 characters long")
    
    if not any(c.isupper() for c in password):
        issues.append("Password must contain at least one uppercase letter")
    
    if not any(c.islower() for c in password):
        issues.append("Password must contain at least one lowercase letter")
    
    if not any(c.isdigit() for c in password):
        issues.append("Password must contain at least one digit")
    
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        issues.append("Password must contain at least one special character")
    
    # Check for common passwords
    common_passwords = [
        "password", "123456", "password123", "admin", "letmein",
        "welcome", "monkey", "dragon", "master", "qwerty"
    ]
    if password.lower() in common_passwords:
        issues.append("Password is too common")
    
    return len(issues) == 0, issues


class IPWhitelist:
    """IP address whitelisting for restricted endpoints"""
    
    def __init__(self, allowed_ips: list[str]):
        self.allowed_ips = set(allowed_ips)
    
    def is_allowed(self, ip: str) -> bool:
        """Check if IP is whitelisted"""
        return ip in self.allowed_ips or ip == "127.0.0.1"
    
    def add_ip(self, ip: str):
        """Add IP to whitelist"""
        self.allowed_ips.add(ip)
    
    def remove_ip(self, ip: str):
        """Remove IP from whitelist"""
        self.allowed_ips.discard(ip)


def get_client_ip(request: Request) -> str:
    """
    Get client IP address from request
    Handles proxies and load balancers
    """
    # Check X-Forwarded-For header (from proxies)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Get first IP in chain
        return forwarded_for.split(",")[0].strip()
    
    # Check X-Real-IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fall back to direct connection
    if request.client:
        return request.client.host
    
    return "unknown"
