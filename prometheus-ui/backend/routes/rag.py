"""
RAG query routes
"""
import logging
import time
from fastapi import APIRouter, HTTPException, Request, UploadFile, File
from slowapi import Limiter
from slowapi.util import get_remote_address

from models.schemas import RagRequest, RagResponse, TranscriptionResponse
from services import rag_service, whisper_service, cache_service, analytics_service, user_history_service

logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create router
router = APIRouter(tags=["RAG"])


@router.post("/rag", response_model=RagResponse)
@limiter.limit("100/minute")
async def query_rag(request: Request, rag_data: RagRequest):
    """Execute RAG query with caching and analytics"""
    logger.info(f"RAG query from user {rag_data.user_id}: '{rag_data.query[:50]}...'")
    
    start_time = time.time()
    cached = False
    
    try:
        # Check cache first
        filters = getattr(rag_data, 'filters', None)
        cached_result = cache_service.get_cached_response(rag_data.query, rag_data.lang, filters)
        
        if cached_result:
            result = cached_result
            cached = True
        else:
            # Query RAG service
            result = rag_service.query(rag_data.query, rag_data.lang, filters)
            
            # Cache the result
            cache_service.cache_response(rag_data.query, result, rag_data.lang, filters)
        
        # Track analytics
        response_time = time.time() - start_time
        if rag_data.user_id:
            analytics_service.track_query(
                user_id=rag_data.user_id,
                query=rag_data.query,
                lang=rag_data.lang,
                response_time=response_time,
                sources_count=len(result.get("sources", [])),
                cached=cached
            )
            
            # Save to user history
            user_history_service.save_query(
                user_id=rag_data.user_id,
                query=rag_data.query,
                language=rag_data.lang,
                response=result["answer"],
                response_time=response_time,
                sources_count=len(result.get("sources", [])),
                cached=cached,
                filters=filters
            )
        
        return {
            "answer": result["answer"],
            "sources": result["sources"]
        }
    
    except Exception as e:
        logger.error(f"RAG query error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process query")


@router.post("/transcribe", response_model=TranscriptionResponse)
@limiter.limit("20/minute")
async def transcribe_audio(request: Request, audio: UploadFile = File(...)):
    """Transcribe audio to text using Whisper"""
    logger.info(f"Transcription request: {audio.filename}")
    
    try:
        # Read audio data
        audio_data = await audio.read()
        
        # Transcribe
        transcription = whisper_service.transcribe_audio(audio_data)
        
        return {
            "transcription": transcription,
            "success": True
        }
    
    except Exception as e:
        logger.error(f"Transcription error: {str(e)}")
        raise HTTPException(status_code=500, detail="Transcription failed")


@router.get("/company/{company_name}")
@limiter.limit("50/minute")
async def get_company_info(request: Request, company_name: str, lang: str = "en"):
    """Get detailed company information"""
    logger.info(f"Company info request: {company_name}")
    
    company_info = rag_service.get_company_info(company_name, lang)
    
    if company_info is None:
        raise HTTPException(status_code=404, detail="Company not found")
    
    return company_info
