"""
Chat history routes
"""
import logging
from fastapi import APIRouter, HTTPException
from typing import List

from models.schemas import ChatMessage, SaveChatRequest
from database import get_chat_history, save_chat, clear_chat_history

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/chat", tags=["Chat History"])


@router.get("/{user_id}/history")
async def get_chat(user_id: int, limit: int = 50, offset: int = 0):
    """Get user's chat history"""
    logger.info(f"Fetching chat history for user {user_id}")
    
    try:
        history = get_chat_history(user_id, limit=limit, offset=offset)
        return history
    
    except Exception as e:
        logger.error(f"Error fetching chat history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch chat history")


@router.post("/{user_id}/save")
async def save_chat_message(user_id: int, chat_data: SaveChatRequest):
    """Save chat message"""
    logger.info(f"Saving chat for user {user_id}")
    
    try:
        save_chat(user_id, chat_data.query, "en", chat_data.response)
        return {"success": True, "message": "Chat saved successfully"}
    
    except Exception as e:
        logger.error(f"Error saving chat: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save chat")


@router.delete("/{user_id}/clear")
async def clear_chat(user_id: int):
    """Clear user's chat history"""
    logger.info(f"Clearing chat history for user {user_id}")
    
    try:
        deleted_count = clear_chat_history(user_id)
        return {"success": True, "message": f"Deleted {deleted_count} messages"}
    
    except Exception as e:
        logger.error(f"Error clearing chat: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to clear chat history")
