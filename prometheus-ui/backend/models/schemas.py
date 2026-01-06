"""
Pydantic models for request/response schemas
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

# Authentication Models
class SignupRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class AuthResponse(BaseModel):
    success: bool
    message: str
    user_id: Optional[int] = None
    username: Optional[str] = None
    token: Optional[str] = None

# RAG Models
class RagRequest(BaseModel):
    query: str
    lang: Optional[str] = "en"
    user_id: Optional[int] = None
    filters: Optional[dict] = None  # {"sector": "FinTech", "min_amount": 1000000, etc.}

class RagResponse(BaseModel):
    answer: str
    sources: List[dict]

# Chat History Models
class SaveChatRequest(BaseModel):
    query: str
    response: str

class ChatMessage(BaseModel):
    query: str
    response: str
    timestamp: str

class ChatHistoryResponse(BaseModel):
    history: List[ChatMessage]

# Transcription Models
class TranscriptionResponse(BaseModel):
    transcription: str
    success: bool

# Company Info Models
class CompanyInfoResponse(BaseModel):
    company: str
    description: str
    funding_rounds: List[dict]
    total_funding: str
    total_rounds: int

# Health Check Models
class HealthCheckResponse(BaseModel):
    status: str
    timestamp: str
    version: str

class MetricsResponse(BaseModel):
    uptime_seconds: int
    status: str
    timestamp: str

# Export Models
class ExportRequest(BaseModel):
    sources: List[dict]
