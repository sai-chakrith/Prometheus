"""
PROMETHEUS FastAPI Backend - Full Enhanced Version
Multilingual Startup Funding Query System
With Advanced Features: Caching, Analytics, Webhooks, A/B Testing, etc.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from config import Config
from services import (
    rag_service, whisper_service, cache_service,
    analytics_service, email_service, translation_service
)
from routes import auth, rag, chat, health, export, websocket, history

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address) if Config.RATE_LIMIT_ENABLED else None

# Create FastAPI app
app = FastAPI(
    title="Prometheus RAG API - Enhanced",
    version="3.0.0",
    description="Multilingual Startup Funding Query System with Advanced Features",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc
)

# Add rate limiter to app state
if limiter:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("=" * 60)
    logger.info("Starting Prometheus RAG API v3.0 (Enhanced)")
    logger.info("=" * 60)
    
    # Initialize RAG service
    logger.info("📊 Initializing RAG service...")
    dataset_path = Config.DATASET_PATH
    rag_service.initialize(dataset_path)
    logger.info("✅ RAG service ready")
    
    # Initialize Whisper service
    logger.info("🎤 Initializing Whisper STT model...")
    whisper_service.initialize(
        model_size=Config.WHISPER_MODEL_SIZE,
        device=Config.WHISPER_DEVICE,
        compute_type=Config.WHISPER_COMPUTE_TYPE
    )
    logger.info("✅ Whisper service ready")
    
    # Initialize cache service (Redis)
    logger.info("🚀 Initializing cache service...")
    try:
        cache_service.initialize()
        if cache_service.enabled:
            logger.info("✅ Redis cache ready")
        else:
            logger.info("⚠️  Redis cache disabled (optional)")
    except Exception as e:
        logger.warning(f"⚠️  Cache initialization skipped: {e}")
    
    logger.info("=" * 60)
    logger.info("🎉 All services initialized successfully!")
    logger.info("📚 API Documentation: http://localhost:8000/docs")
    logger.info("🔗 ReDoc: http://localhost:8000/redoc")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Prometheus RAG API...")
    
    # Invalidate cache
    if cache_service.enabled:
        logger.info("Clearing cache...")
    
    logger.info("Shutdown complete")


# Register routers
app.include_router(auth.router)
app.include_router(rag.router)
app.include_router(chat.router)
app.include_router(health.router)
app.include_router(export.router)
app.include_router(websocket.router)
app.include_router(history.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Prometheus RAG API - Enhanced Edition",
        "version": "3.0.0",
        "status": "online",
        "features": [
            "🔐 JWT Authentication",
            "⚡ Redis Caching",
            "📊 Analytics Tracking",
            "🔔 Webhooks & Email Notifications",
            "🌍 Advanced Translation",
            "📤 Export (CSV/Excel/JSON)",
            "🔄 Real-time WebSocket",
            "🧪 A/B Testing Framework",
            "⏰ Background Jobs (Celery)"
        ],
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }


@app.get("/cache/stats")
async def cache_stats():
    """Get cache statistics"""
    return cache_service.get_cache_stats()


@app.post("/cache/clear")
async def clear_cache():
    """Clear all cache"""
    deleted = cache_service.invalidate_cache()
    return {"success": True, "deleted_keys": deleted}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_enhanced:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG
    )
