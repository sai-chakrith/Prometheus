# -*- coding: utf-8 -*-
"""
FastAPI Backend for Startup Funding Intelligence
Provides RESTful API endpoints for querying funding data
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import traceback
from datetime import datetime

# Import query router
from src.query_router import process_query, initialize, detect_intent, extract_filters


# Pydantic Models
class QueryRequest(BaseModel):
    """Request model for query endpoint."""
    query: str = Field(..., min_length=1, description="User query in English or Hindi")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "कर्नाटक में फिनटेक फंडिंग?"
            }
        }


class QueryResponse(BaseModel):
    """Response model for query endpoint."""
    answer: str = Field(..., description="Formatted answer to the query")
    sources: List[str] = Field(default_factory=list, description="Source citations or data points")
    intent: Optional[str] = Field(None, description="Detected intent: 'analytics' or 'rag'")
    filters: Optional[Dict[str, Any]] = Field(None, description="Extracted filters from query")
    timestamp: str = Field(..., description="Response timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "📊 Funding Statistics:\n...",
                "sources": ["Karnataka fintech sector", "2022 data"],
                "intent": "analytics",
                "filters": {"sector": "fintech", "state": "karnataka"},
                "timestamp": "2025-12-29T10:30:00"
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(..., description="API status")
    message: str = Field(..., description="Status message")
    timestamp: str = Field(..., description="Current timestamp")
    version: str = Field(default="1.0.0", description="API version")


# Initialize FastAPI app
app = FastAPI(
    title="Startup Funding Intelligence API",
    description="Multilingual RAG-based API for Indian Startup Funding Data Analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global initialization flag
_initialized = False


def ensure_initialized():
    """Ensure the query router is initialized."""
    global _initialized
    if not _initialized:
        try:
            print("Initializing query router on first request...")
            initialize()
            _initialized = True
            print("✅ Query router initialized successfully!")
        except Exception as e:
            print(f"❌ Failed to initialize query router: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to initialize system: {str(e)}"
            )


@app.on_event("startup")
async def startup_event():
    """Initialize system on startup."""
    print("="*70)
    print("🚀 Starting Startup Funding Intelligence API")
    print("="*70)
    try:
        ensure_initialized()
        print("✅ API is ready to accept requests!")
    except Exception as e:
        print(f"⚠️ Warning: Startup initialization failed: {str(e)}")
        print("Will attempt to initialize on first request.")
    print("="*70)


@app.get("/", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        HealthResponse: API health status
    """
    return HealthResponse(
        status="healthy",
        message="Startup Funding Intelligence API is running",
        timestamp=datetime.now().isoformat()
    )


@app.get("/health", response_model=HealthResponse)
async def detailed_health_check():
    """
    Detailed health check endpoint with initialization status.
    
    Returns:
        HealthResponse: Detailed API health status
    """
    global _initialized
    
    if _initialized:
        message = "API is fully initialized and ready"
        api_status = "healthy"
    else:
        message = "API is running but not yet initialized"
        api_status = "initializing"
    
    return HealthResponse(
        status=api_status,
        message=message,
        timestamp=datetime.now().isoformat()
    )


@app.post("/ask", response_model=QueryResponse)
async def ask_query(request: QueryRequest):
    """
    Process user query and return intelligent response.
    
    Supports:
    - English and Hindi queries
    - Analytics queries (statistics, trends, counts)
    - RAG queries (specific information retrieval)
    - Automatic filter extraction (sector, state, year)
    
    Args:
        request: QueryRequest with user query
        
    Returns:
        QueryResponse: Formatted answer with sources and metadata
        
    Raises:
        HTTPException: If query processing fails
    """
    try:
        # Ensure system is initialized
        ensure_initialized()
        
        # Validate query
        if not request.query or not request.query.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query cannot be empty"
            )
        
        # Detect intent and extract filters
        intent = detect_intent(request.query)
        filters = extract_filters(request.query)
        
        # Process query
        answer = process_query(request.query)
        
        # Extract sources from filters
        sources = []
        if filters:
            if 'sector' in filters:
                sources.append(f"Sector: {filters['sector']}")
            if 'state' in filters:
                sources.append(f"State: {filters['state']}")
            if 'year' in filters:
                sources.append(f"Year: {filters['year']}")
            if 'round_type' in filters:
                sources.append(f"Round: {filters['round_type']}")
        
        # If no sources from filters, indicate data source
        if not sources:
            sources = ["Indian Startup Funding Dataset (2015-2021)"]
        
        return QueryResponse(
            answer=answer,
            sources=sources,
            intent=intent,
            filters=filters,
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        # Log error
        error_trace = traceback.format_exc()
        print(f"❌ Error processing query: {str(e)}")
        print(error_trace)
        
        # Return user-friendly error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )


@app.get("/info")
async def api_info():
    """
    Get API information and supported features.
    
    Returns:
        dict: API capabilities and usage information
    """
    return {
        "name": "Startup Funding Intelligence API",
        "version": "1.0.0",
        "description": "Multilingual RAG-based API for Indian Startup Funding Data",
        "features": {
            "languages": ["English", "Hindi"],
            "query_types": ["analytics", "rag"],
            "analytics_keywords": [
                "how many", "total", "कितना", "कुल",
                "trend", "average", "औसत", "statistics"
            ],
            "supported_filters": {
                "sectors": ["fintech", "healthtech", "edtech", "e-commerce", "saas", "logistics"],
                "states": ["karnataka", "maharashtra", "delhi", "tamil nadu", "telangana"],
                "years": "2015-2021",
                "round_types": ["seed", "series a", "series b", "series c"]
            }
        },
        "endpoints": {
            "POST /ask": "Submit a query",
            "GET /": "Health check",
            "GET /health": "Detailed health check",
            "GET /info": "API information"
        },
        "example_queries": [
            "कर्नाटक में फिनटेक फंडिंग?",
            "How many fintech startups in Karnataka?",
            "Total funding in 2020",
            "Show me healthtech investments in Bangalore",
            "Top investors in e-commerce sector"
        ]
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return {
        "error": "Not Found",
        "message": "The requested endpoint does not exist",
        "available_endpoints": ["/", "/health", "/ask", "/info", "/docs"]
    }


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors."""
    return {
        "error": "Internal Server Error",
        "message": "An unexpected error occurred. Please try again later.",
        "support": "Check /docs for API documentation"
    }


if __name__ == "__main__":
    import uvicorn
    
    print("="*70)
    print("Starting Startup Funding Intelligence API Server")
    print("="*70)
    print("Documentation available at: http://localhost:8000/docs")
    print("="*70)
    
    uvicorn.run(
        "app.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes (disable in production)
        log_level="info"
    )
