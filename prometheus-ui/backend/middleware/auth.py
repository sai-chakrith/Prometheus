"""
JWT Authentication Middleware
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict
from fastapi import Header, HTTPException, Depends
from jose import jwt, JWTError
from config import Config

logger = logging.getLogger(__name__)

# JWT Configuration
SECRET_KEY = Config.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


def create_jwt_token(user_id: int, username: str, email: str = None) -> str:
    """
    Create JWT access token
    
    Args:
        user_id: User ID
        username: Username
        email: Email (optional)
    
    Returns:
        JWT token string
    """
    payload = {
        "user_id": user_id,
        "username": username,
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS),
        "iat": datetime.utcnow()
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    logger.debug(f"Created JWT token for user {username}")
    return token


def decode_jwt_token(token: str) -> Optional[Dict]:
    """
    Decode and validate JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded payload dict or None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check expiration
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
            logger.warning("Token expired")
            return None
        
        return payload
    
    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        return None


async def verify_jwt_token(authorization: str = Header(None)) -> Dict:
    """
    Verify JWT token from Authorization header
    
    Dependency for protected routes
    
    Usage:
        @router.get("/protected")
        async def protected_route(user: Dict = Depends(verify_jwt_token)):
            return {"user_id": user["user_id"]}
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Extract token from "Bearer <token>"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication scheme"
            )
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format"
        )
    
    # Decode and validate token
    payload = decode_jwt_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return payload


async def optional_jwt_token(authorization: str = Header(None)) -> Optional[Dict]:
    """
    Optional JWT verification
    
    Returns user info if token present and valid, None otherwise
    """
    if not authorization:
        return None
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() == "bearer":
            return decode_jwt_token(token)
    except:
        pass
    
    return None


def refresh_jwt_token(token: str) -> Optional[str]:
    """
    Refresh JWT token if valid
    
    Args:
        token: Current JWT token
    
    Returns:
        New JWT token or None if invalid
    """
    payload = decode_jwt_token(token)
    
    if not payload:
        return None
    
    # Create new token with same data
    return create_jwt_token(
        user_id=payload["user_id"],
        username=payload["username"],
        email=payload.get("email")
    )
