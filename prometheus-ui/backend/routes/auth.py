"""
Authentication routes
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from models.schemas import SignupRequest, LoginRequest, AuthResponse
from database import create_user, authenticate_user
from middleware import create_jwt_token
from services import email_service

logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create router
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=AuthResponse)
@limiter.limit("5/minute")
async def signup(request: Request, signup_data: SignupRequest):
    """Register a new user"""
    logger.info(f"Signup attempt: {signup_data.username}")
    
    try:
        result = create_user(signup_data.username, signup_data.email, signup_data.password)
        
        if not result['success']:
            logger.warning(f"Signup failed: {result.get('error')}")
            raise HTTPException(status_code=400, detail=result.get('error'))
        
        logger.info(f"User created successfully: {signup_data.username} (ID: {result['user_id']})")
        
        # Create JWT token
        token = create_jwt_token(result['user_id'], result['username'], result.get('email'))
        
        # Send welcome email asynchronously
        try:
            email_service.send_welcome_email(result.get('email'), result['username'])
        except Exception as e:
            logger.warning(f"Failed to send welcome email: {e}")
        
        return {
            "success": True,
            "message": "User created successfully",
            "user_id": result['user_id'],
            "username": result['username'],
            "token": token
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/login", response_model=AuthResponse)
@limiter.limit("5/minute")
async def login(request: Request, login_data: LoginRequest):
    """Authenticate user"""
    logger.info(f"Login attempt: {login_data.username}")
    
    result = authenticate_user(login_data.username, login_data.password)
    
    if result:
        logger.info(f"Login successful: {login_data.username} (ID: {result['user_id']})")
        
        # Create JWT token
        token = create_jwt_token(result['user_id'], result['username'], result.get('email'))
        
        return {
            "success": True,
            "message": "Login successful",
            "user_id": result['user_id'],
            "username": result['username'],
            "token": token
        }
    
    logger.warning(f"Login failed: invalid credentials for {login_data.username}")
    raise HTTPException(status_code=401, detail="Invalid credentials")


@router.post("/logout")
async def logout():
    """Logout user (client-side session clear)"""
    return {"success": True, "message": "Logged out successfully"}
