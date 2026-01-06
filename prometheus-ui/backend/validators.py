"""
Input validation utilities for Prometheus RAG
"""
import re
from typing import Tuple
from pydantic import BaseModel, field_validator, EmailStr, Field

class SignupRequestValidated(BaseModel):
    """Validated signup request"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username can only contain letters, numbers, underscores, and hyphens')
        return v.strip()
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v

class RagRequestValidated(BaseModel):
    """Validated RAG query request"""
    query: str = Field(..., min_length=1, max_length=1000)
    lang: str = Field(default="en", pattern=r'^(en|hi|te|ta|kn|mr|gu|bn)$')
    
    @field_validator('query')
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Sanitize and validate query"""
        # Remove potentially dangerous characters
        v = v.strip()
        if not v:
            raise ValueError('Query cannot be empty')
        
        # Check for SQL injection patterns
        dangerous_patterns = [
            r';\s*DROP\s+TABLE',
            r';\s*DELETE\s+FROM',
            r';\s*UPDATE\s+',
            r'<script',
            r'javascript:',
        ]
        for pattern in dangerous_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError('Invalid query content detected')
        
        return v

class SaveChatRequestValidated(BaseModel):
    """Validated save chat request"""
    query: str = Field(..., max_length=1000)
    lang: str = Field(..., pattern=r'^(en|hi|te|ta|kn|mr|gu|bn)$')
    response: str = Field(..., max_length=10000)

def sanitize_html(text: str) -> str:
    """Remove HTML tags from text"""
    return re.sub(r'<[^>]+>', '', text)

def validate_file_upload(filename: str, allowed_extensions: set) -> Tuple[bool, str]:
    """Validate file upload"""
    if not filename:
        return False, "No filename provided"
    
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if ext not in allowed_extensions:
        return False, f"File type .{ext} not allowed. Allowed: {', '.join(allowed_extensions)}"
    
    return True, "Valid file"
