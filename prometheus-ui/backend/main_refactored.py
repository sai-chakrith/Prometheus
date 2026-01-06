"""
PROMETHEUS FastAPI Backend - Refactored Modular Version
Multilingual Startup Funding Query System
Enhanced with ChromaDB + Ollama Llama 3.1 8B + RAGAS Evaluation
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from config import Config
from services import rag_service, whisper_service
from routes import auth, rag, chat, health

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
    title="Prometheus RAG API",
    version="2.0.0",
    description="Multilingual Startup Funding Query System with RAG"
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
    logger.info("Starting Prometheus RAG API...")
    
    # Initialize RAG service
    dataset_path = Config.DATASET_PATH
    logger.info(f"Loading dataset from: {dataset_path}")
    rag_service.initialize(dataset_path)
    
    # Initialize Whisper service
    logger.info("Initializing Whisper STT model...")
    whisper_service.initialize(
        model_size=Config.WHISPER_MODEL_SIZE,
        device=Config.WHISPER_DEVICE,
        compute_type=Config.WHISPER_COMPUTE_TYPE
    )
    
    logger.info("All services initialized successfully!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Prometheus RAG API...")


# Register routers
app.include_router(auth.router)
app.include_router(rag.router)
app.include_router(chat.router)
app.include_router(health.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Prometheus RAG API",
        "version": "2.0.0",
        "status": "online"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG
    )
