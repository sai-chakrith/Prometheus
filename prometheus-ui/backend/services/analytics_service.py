"""
Analytics Service - Track usage, queries, and performance metrics
"""
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from database import get_db_connection

logger = logging.getLogger(__name__)


def init_analytics_tables():
    """Initialize analytics tables"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Query analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                query TEXT NOT NULL,
                language TEXT DEFAULT 'en',
                response_time REAL,
                sources_count INTEGER,
                cached BOOLEAN DEFAULT 0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create index for performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_analytics_user 
            ON analytics(user_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_analytics_timestamp 
            ON analytics(timestamp)
        ''')
        
        conn.commit()
        logger.info("Analytics tables initialized")


class AnalyticsService:
    """Service for tracking and analyzing usage metrics"""
    
    def track_query(self, user_id: int, query: str, lang: str = "en",
                   response_time: float = 0.0, sources_count: int = 0,
                   cached: bool = False):
        """
        Track a RAG query
        
        Args:
            user_id: User ID
            query: Query text
            lang: Language code
            response_time: Response time in seconds
            sources_count: Number of sources returned
            cached: Whether response was cached
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO analytics 
                    (user_id, query, language, response_time, sources_count, cached, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, query, lang, response_time, sources_count, cached, datetime.now()))
                conn.commit()
                logger.debug(f"Tracked query for user {user_id}")
        
        except Exception as e:
            logger.error(f"Error tracking query: {e}")
    
    def get_popular_queries(self, limit: int = 10, days: int = 30) -> List[Dict]:
        """
        Get most popular queries
        
        Args:
            limit: Number of results
            days: Time window in days
        
        Returns:
            List of {query, count, avg_response_time}
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT 
                        query,
                        COUNT(*) as count,
                        AVG(response_time) as avg_response_time,
                        language
                    FROM analytics 
                    WHERE timestamp > ?
                    GROUP BY query, language
                    ORDER BY count DESC 
                    LIMIT ?
                ''', (cutoff_date, limit))
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        "query": row[0],
                        "count": row[1],
                        "avg_response_time": round(row[2], 3) if row[2] else 0,
                        "language": row[3]
                    })
                
                return results
        
        except Exception as e:
            logger.error(f"Error fetching popular queries: {e}")
            return []
    
    def get_user_stats(self, user_id: int) -> Dict:
        """
        Get statistics for a specific user
        
        Args:
            user_id: User ID
        
        Returns:
            Dict with total_queries, avg_response_time, preferred_language, etc.
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Overall stats
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_queries,
                        AVG(response_time) as avg_response_time,
                        SUM(CASE WHEN cached = 1 THEN 1 ELSE 0 END) as cached_queries
                    FROM analytics 
                    WHERE user_id = ?
                ''', (user_id,))
                
                row = cursor.fetchone()
                
                # Preferred language
                cursor.execute('''
                    SELECT language, COUNT(*) as count
                    FROM analytics 
                    WHERE user_id = ?
                    GROUP BY language
                    ORDER BY count DESC
                    LIMIT 1
                ''', (user_id,))
                
                lang_row = cursor.fetchone()
                
                return {
                    "user_id": user_id,
                    "total_queries": row[0] or 0,
                    "avg_response_time": round(row[1], 3) if row[1] else 0,
                    "cached_queries": row[2] or 0,
                    "cache_hit_rate": round((row[2] / row[0] * 100) if row[0] > 0 else 0, 2),
                    "preferred_language": lang_row[0] if lang_row else "en"
                }
        
        except Exception as e:
            logger.error(f"Error fetching user stats: {e}")
            return {}
    
    def get_system_stats(self, days: int = 7) -> Dict:
        """
        Get overall system statistics
        
        Args:
            days: Time window in days
        
        Returns:
            Dict with system-wide metrics
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_queries,
                        COUNT(DISTINCT user_id) as active_users,
                        AVG(response_time) as avg_response_time,
                        SUM(CASE WHEN cached = 1 THEN 1 ELSE 0 END) as cached_queries
                    FROM analytics 
                    WHERE timestamp > ?
                ''', (cutoff_date,))
                
                row = cursor.fetchone()
                
                # Queries per day
                cursor.execute('''
                    SELECT 
                        DATE(timestamp) as date,
                        COUNT(*) as count
                    FROM analytics 
                    WHERE timestamp > ?
                    GROUP BY DATE(timestamp)
                    ORDER BY date DESC
                ''', (cutoff_date,))
                
                daily_queries = [{"date": row[0], "count": row[1]} for row in cursor.fetchall()]
                
                return {
                    "period_days": days,
                    "total_queries": row[0] or 0,
                    "active_users": row[1] or 0,
                    "avg_response_time": round(row[2], 3) if row[2] else 0,
                    "cached_queries": row[2] or 0,
                    "cache_hit_rate": round((row[3] / row[0] * 100) if row[0] > 0 else 0, 2),
                    "daily_breakdown": daily_queries
                }
        
        except Exception as e:
            logger.error(f"Error fetching system stats: {e}")
            return {}
    
    def get_language_distribution(self, days: int = 30) -> List[Dict]:
        """Get query distribution by language"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT 
                        language,
                        COUNT(*) as count,
                        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
                    FROM analytics 
                    WHERE timestamp > ?
                    GROUP BY language
                    ORDER BY count DESC
                ''', (cutoff_date,))
                
                return [
                    {"language": row[0], "count": row[1], "percentage": row[2]}
                    for row in cursor.fetchall()
                ]
        
        except Exception as e:
            logger.error(f"Error fetching language distribution: {e}")
            return []


# Global analytics service instance
analytics_service = AnalyticsService()


# Initialize tables on import
try:
    init_analytics_tables()
except Exception as e:
    logger.error(f"Failed to initialize analytics tables: {e}")
