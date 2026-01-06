"""
WebSocket routes - Real-time updates
"""
import logging
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter(tags=["WebSocket"])


class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[int, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int = None):
        """Accept and store websocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = []
            self.user_connections[user_id].append(websocket)
        
        logger.info(f"WebSocket connected (user_id: {user_id}). Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket, user_id: int = None):
        """Remove websocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        if user_id and user_id in self.user_connections:
            if websocket in self.user_connections[user_id]:
                self.user_connections[user_id].remove(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        logger.info(f"WebSocket disconnected. Remaining: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific websocket"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
    
    async def send_to_user(self, message: dict, user_id: int):
        """Send message to all connections of a specific user"""
        if user_id in self.user_connections:
            message_text = json.dumps(message)
            for connection in self.user_connections[user_id]:
                try:
                    await connection.send_text(message_text)
                except Exception as e:
                    logger.error(f"Error sending to user {user_id}: {e}")
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        message_text = json.dumps(message)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_text)
            except Exception as e:
                logger.error(f"Error broadcasting: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)


# Global connection manager
manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, user_id: int = None):
    """
    WebSocket endpoint for real-time updates
    
    Usage:
        ws://localhost:8000/ws?user_id=123
    
    Message format:
        {
            "type": "ping|subscribe|unsubscribe",
            "data": {}
        }
    """
    await manager.connect(websocket, user_id)
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "message": "WebSocket connected successfully",
            "user_id": user_id
        })
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                message_type = message.get("type")
                
                if message_type == "ping":
                    # Heartbeat
                    await websocket.send_json({"type": "pong"})
                
                elif message_type == "subscribe":
                    # Subscribe to specific events
                    events = message.get("events", [])
                    await websocket.send_json({
                        "type": "subscribed",
                        "events": events
                    })
                
                elif message_type == "query":
                    # Real-time query (could integrate with RAG)
                    await websocket.send_json({
                        "type": "query_received",
                        "status": "processing"
                    })
                
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Unknown message type: {message_type}"
                    })
            
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON"
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        logger.info(f"Client disconnected (user_id: {user_id})")
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, user_id)


async def notify_new_startup(startup_data: dict):
    """
    Send new startup notification to all connected clients
    
    This can be called from other parts of the application
    """
    await manager.broadcast({
        "type": "new_startup",
        "data": startup_data
    })


async def notify_user(user_id: int, notification: dict):
    """Send notification to specific user"""
    await manager.send_to_user({
        "type": "notification",
        "data": notification
    }, user_id)


# Background task to send periodic updates
async def send_periodic_stats():
    """Send periodic statistics to all connected clients"""
    while True:
        await asyncio.sleep(60)  # Every 60 seconds
        
        if manager.active_connections:
            from services.analytics_service import analytics_service
            
            try:
                stats = analytics_service.get_system_stats(days=1)
                await manager.broadcast({
                    "type": "stats_update",
                    "data": stats
                })
            except Exception as e:
                logger.error(f"Error sending periodic stats: {e}")
