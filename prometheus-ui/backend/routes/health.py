"""
Health check and metrics routes
"""
import logging
import time
from fastapi import APIRouter
from datetime import datetime

from models.schemas import HealthCheckResponse, MetricsResponse

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(tags=["Health"])

# Track startup time
_startup_time = time.time()


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Get system metrics"""
    uptime_seconds = int(time.time() - _startup_time)
    
    return {
        "uptime_seconds": uptime_seconds,
        "status": "operational",
        "timestamp": datetime.now().isoformat()
    }
