"""
User History Routes
Endpoints for managing user query history and preferences
"""

import logging
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from services import user_history_service
from models.schemas import AuthResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/history", tags=["User History"])


@router.get("/{user_id}")
async def get_query_history(
    user_id: int,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    language: Optional[str] = None,
    search: Optional[str] = None,
    days: Optional[int] = None
):
    """
    Get user's query history with pagination and filters
    
    - **limit**: Number of results per page (1-100)
    - **offset**: Offset for pagination
    - **language**: Filter by language code (en, hi, te, ta, etc.)
    - **search**: Search in queries and responses
    - **days**: Only show history from last N days
    """
    logger.info(f"Fetching query history for user {user_id}")
    
    try:
        history = user_history_service.get_query_history(
            user_id=user_id,
            limit=limit,
            offset=offset,
            language=language,
            search=search,
            days=days
        )
        
        return {
            "success": True,
            **history
        }
    
    except Exception as e:
        logger.error(f"Error fetching history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch query history")


@router.delete("/{user_id}/query/{query_id}")
async def delete_query(user_id: int, query_id: int):
    """Delete a specific query from history"""
    logger.info(f"Deleting query {query_id} for user {user_id}")
    
    try:
        deleted = user_history_service.delete_query_from_history(query_id, user_id)
        
        if deleted:
            return {
                "success": True,
                "message": "Query deleted from history"
            }
        else:
            raise HTTPException(status_code=404, detail="Query not found or unauthorized")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting query: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete query")


@router.delete("/{user_id}/clear")
async def clear_history(
    user_id: int,
    days: Optional[int] = Query(None, description="Clear history older than N days")
):
    """Clear user's query history (optionally older than N days)"""
    logger.info(f"Clearing history for user {user_id} (days={days})")
    
    try:
        deleted_count = user_history_service.clear_history(user_id, days)
        
        return {
            "success": True,
            "message": f"Cleared {deleted_count} queries from history",
            "deleted_count": deleted_count
        }
    
    except Exception as e:
        logger.error(f"Error clearing history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to clear history")


@router.get("/{user_id}/stats")
async def get_user_stats(
    user_id: int,
    days: int = Query(30, ge=1, le=365, description="Stats period in days")
):
    """
    Get comprehensive user statistics
    
    Returns:
    - Total queries
    - Average response time
    - Cache hit rate
    - Most used language
    - Daily activity
    - Popular queries
    """
    logger.info(f"Fetching stats for user {user_id} (last {days} days)")
    
    try:
        stats = user_history_service.get_user_stats(user_id, days)
        
        return {
            "success": True,
            **stats
        }
    
    except Exception as e:
        logger.error(f"Error fetching stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch user stats")


@router.post("/{user_id}/favorites")
async def save_favorite(
    user_id: int,
    query: str,
    title: Optional[str] = None,
    filters: Optional[dict] = None
):
    """Save a query as favorite"""
    logger.info(f"Saving favorite query for user {user_id}")
    
    try:
        favorite_id = user_history_service.save_favorite_query(
            user_id=user_id,
            query=query,
            title=title,
            filters=filters
        )
        
        if favorite_id:
            return {
                "success": True,
                "message": "Query saved to favorites",
                "favorite_id": favorite_id
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to save favorite")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving favorite: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save favorite query")


@router.get("/{user_id}/favorites")
async def get_favorites(user_id: int):
    """Get user's favorite queries"""
    logger.info(f"Fetching favorites for user {user_id}")
    
    try:
        favorites = user_history_service.get_favorite_queries(user_id)
        
        return {
            "success": True,
            "favorites": favorites,
            "count": len(favorites)
        }
    
    except Exception as e:
        logger.error(f"Error fetching favorites: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch favorites")


@router.get("/{user_id}/preferences")
async def get_preferences(user_id: int):
    """Get user preferences"""
    logger.info(f"Fetching preferences for user {user_id}")
    
    try:
        preferences = user_history_service.get_user_preferences(user_id)
        
        return {
            "success": True,
            **preferences
        }
    
    except Exception as e:
        logger.error(f"Error fetching preferences: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch preferences")


@router.put("/{user_id}/preferences")
async def update_preferences(user_id: int, preferences: dict):
    """
    Update user preferences
    
    Supported preferences:
    - preferred_language: Default language (en, hi, te, ta, etc.)
    - preferred_sectors: Comma-separated sectors
    - preferred_locations: Comma-separated locations
    - notification_settings: JSON string of notification settings
    - theme: UI theme (light, dark)
    """
    logger.info(f"Updating preferences for user {user_id}")
    
    try:
        success = user_history_service.update_user_preferences(user_id, preferences)
        
        if success:
            return {
                "success": True,
                "message": "Preferences updated successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to update preferences")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating preferences: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update preferences")


@router.post("/{user_id}/activity")
async def log_activity(
    user_id: int,
    activity_type: str,
    details: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
):
    """Log user activity"""
    try:
        success = user_history_service.log_activity(
            user_id=user_id,
            activity_type=activity_type,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        if success:
            return {"success": True, "message": "Activity logged"}
        else:
            raise HTTPException(status_code=500, detail="Failed to log activity")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging activity: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to log activity")
