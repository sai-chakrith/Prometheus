"""
Webhook Service - External integrations and notifications
"""
import logging
import httpx
from typing import List, Dict, Optional
from datetime import datetime
from database import get_db_connection

logger = logging.getLogger(__name__)


def init_webhook_tables():
    """Initialize webhook tables"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS webhooks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                url TEXT NOT NULL,
                event_type TEXT NOT NULL,
                active BOOLEAN DEFAULT 1,
                secret TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS webhook_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                webhook_id INTEGER,
                event_type TEXT,
                payload TEXT,
                status_code INTEGER,
                response TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (webhook_id) REFERENCES webhooks (id)
            )
        ''')
        
        conn.commit()
        logger.info("Webhook tables initialized")


class WebhookService:
    """Service for managing and triggering webhooks"""
    
    def register_webhook(self, user_id: int, url: str, event_type: str, 
                        secret: Optional[str] = None) -> int:
        """
        Register a new webhook
        
        Args:
            user_id: User ID
            url: Webhook URL
            event_type: Event type (new_startup, funding_alert, etc.)
            secret: Optional secret for HMAC verification
        
        Returns:
            Webhook ID
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO webhooks (user_id, url, event_type, secret)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, url, event_type, secret))
                conn.commit()
                
                webhook_id = cursor.lastrowid
                logger.info(f"Registered webhook {webhook_id} for user {user_id}")
                return webhook_id
        
        except Exception as e:
            logger.error(f"Error registering webhook: {e}")
            raise
    
    def get_webhooks(self, user_id: int, event_type: Optional[str] = None) -> List[Dict]:
        """Get webhooks for a user"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                if event_type:
                    cursor.execute('''
                        SELECT id, url, event_type, active, created_at
                        FROM webhooks
                        WHERE user_id = ? AND event_type = ? AND active = 1
                    ''', (user_id, event_type))
                else:
                    cursor.execute('''
                        SELECT id, url, event_type, active, created_at
                        FROM webhooks
                        WHERE user_id = ? AND active = 1
                    ''', (user_id,))
                
                return [
                    {
                        "id": row[0],
                        "url": row[1],
                        "event_type": row[2],
                        "active": bool(row[3]),
                        "created_at": row[4]
                    }
                    for row in cursor.fetchall()
                ]
        
        except Exception as e:
            logger.error(f"Error fetching webhooks: {e}")
            return []
    
    def delete_webhook(self, webhook_id: int, user_id: int) -> bool:
        """Delete a webhook"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE webhooks 
                    SET active = 0 
                    WHERE id = ? AND user_id = ?
                ''', (webhook_id, user_id))
                conn.commit()
                
                return cursor.rowcount > 0
        
        except Exception as e:
            logger.error(f"Error deleting webhook: {e}")
            return False
    
    async def trigger_webhook(self, webhook_id: int, payload: Dict) -> bool:
        """
        Trigger a specific webhook
        
        Args:
            webhook_id: Webhook ID
            payload: Event payload
        
        Returns:
            Success status
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT url, secret FROM webhooks 
                    WHERE id = ? AND active = 1
                ''', (webhook_id,))
                
                row = cursor.fetchone()
                if not row:
                    return False
                
                url, secret = row
            
            # Send HTTP POST request
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {"Content-Type": "application/json"}
                
                # Add HMAC signature if secret provided
                if secret:
                    import hmac
                    import hashlib
                    import json
                    
                    payload_str = json.dumps(payload)
                    signature = hmac.new(
                        secret.encode(),
                        payload_str.encode(),
                        hashlib.sha256
                    ).hexdigest()
                    headers["X-Webhook-Signature"] = signature
                
                response = await client.post(url, json=payload, headers=headers)
                
                # Log webhook delivery
                self._log_webhook(webhook_id, payload, response.status_code, response.text)
                
                logger.info(f"Webhook {webhook_id} triggered: {response.status_code}")
                return response.status_code < 400
        
        except Exception as e:
            logger.error(f"Error triggering webhook {webhook_id}: {e}")
            self._log_webhook(webhook_id, payload, 0, str(e))
            return False
    
    async def trigger_event(self, event_type: str, payload: Dict):
        """
        Trigger all webhooks for an event type
        
        Args:
            event_type: Event type (e.g., 'new_startup')
            payload: Event data
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id FROM webhooks 
                    WHERE event_type = ? AND active = 1
                ''', (event_type,))
                
                webhook_ids = [row[0] for row in cursor.fetchall()]
            
            logger.info(f"Triggering {len(webhook_ids)} webhooks for event '{event_type}'")
            
            # Trigger all webhooks concurrently
            import asyncio
            tasks = [self.trigger_webhook(wid, payload) for wid in webhook_ids]
            await asyncio.gather(*tasks, return_exceptions=True)
        
        except Exception as e:
            logger.error(f"Error triggering event webhooks: {e}")
    
    def _log_webhook(self, webhook_id: int, payload: Dict, status_code: int, response: str):
        """Log webhook delivery"""
        try:
            import json
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO webhook_logs 
                    (webhook_id, event_type, payload, status_code, response)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    webhook_id,
                    payload.get("event"),
                    json.dumps(payload),
                    status_code,
                    response[:500]  # Truncate response
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error logging webhook: {e}")
    
    def get_webhook_logs(self, webhook_id: int, limit: int = 50) -> List[Dict]:
        """Get webhook delivery logs"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT event_type, status_code, response, timestamp
                    FROM webhook_logs
                    WHERE webhook_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (webhook_id, limit))
                
                return [
                    {
                        "event_type": row[0],
                        "status_code": row[1],
                        "response": row[2],
                        "timestamp": row[3]
                    }
                    for row in cursor.fetchall()
                ]
        
        except Exception as e:
            logger.error(f"Error fetching webhook logs: {e}")
            return []


# Global webhook service instance
webhook_service = WebhookService()


# Initialize tables on import
try:
    init_webhook_tables()
except Exception as e:
    logger.error(f"Failed to initialize webhook tables: {e}")
