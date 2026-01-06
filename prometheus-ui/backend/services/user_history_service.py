"""
User History Service
Comprehensive tracking of user interactions, queries, and activity
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from database import get_db_connection

logger = logging.getLogger(__name__)


class UserHistoryService:
    """Service for tracking and managing user history"""
    
    def __init__(self):
        self._initialize_tables()
    
    def _initialize_tables(self):
        """Initialize history tracking tables"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Query history with metadata
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS query_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        query TEXT NOT NULL,
                        language TEXT NOT NULL,
                        response TEXT NOT NULL,
                        response_time REAL,
                        sources_count INTEGER,
                        cached BOOLEAN DEFAULT 0,
                        filters TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                ''')
                
                # User activity log
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_activity (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        activity_type TEXT NOT NULL,
                        details TEXT,
                        ip_address TEXT,
                        user_agent TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                ''')
                
                # User preferences
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_preferences (
                        user_id INTEGER PRIMARY KEY,
                        preferred_language TEXT DEFAULT 'en',
                        preferred_sectors TEXT,
                        preferred_locations TEXT,
                        notification_settings TEXT,
                        theme TEXT DEFAULT 'light',
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                ''')
                
                # Favorite queries/searches
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS favorite_queries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        query TEXT NOT NULL,
                        title TEXT,
                        filters TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                ''')
                
                # Create indexes
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_query_history_user_id 
                    ON query_history(user_id)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_query_history_timestamp 
                    ON query_history(timestamp DESC)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_user_activity_user_id 
                    ON user_activity(user_id)
                ''')
                
                conn.commit()
                logger.info("User history tables initialized")
                
        except Exception as e:
            logger.error(f"Error initializing history tables: {e}")
    
    def save_query(
        self,
        user_id: int,
        query: str,
        language: str,
        response: str,
        response_time: float = 0.0,
        sources_count: int = 0,
        cached: bool = False,
        filters: Optional[Dict] = None
    ) -> bool:
        """Save query to history with metadata"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Convert filters to JSON string
                filters_json = str(filters) if filters else None
                
                cursor.execute('''
                    INSERT INTO query_history 
                    (user_id, query, language, response, response_time, 
                     sources_count, cached, filters)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, query, language, response, response_time,
                      sources_count, cached, filters_json))
                
                conn.commit()
                logger.info(f"Saved query history for user {user_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error saving query history: {e}")
            return False
    
    def get_query_history(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0,
        language: Optional[str] = None,
        search: Optional[str] = None,
        days: Optional[int] = None
    ) -> Dict:
        """Get user's query history with filters and pagination"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Build WHERE clause
                where_clauses = ['user_id = ?']
                params = [user_id]
                
                if language:
                    where_clauses.append('language = ?')
                    params.append(language)
                
                if search:
                    where_clauses.append('(query LIKE ? OR response LIKE ?)')
                    search_pattern = f'%{search}%'
                    params.extend([search_pattern, search_pattern])
                
                if days:
                    cutoff_date = datetime.now() - timedelta(days=days)
                    where_clauses.append('timestamp >= ?')
                    params.append(cutoff_date)
                
                where_clause = ' AND '.join(where_clauses)
                
                # Get total count
                count_query = f'SELECT COUNT(*) FROM query_history WHERE {where_clause}'
                cursor.execute(count_query, params)
                total = cursor.fetchone()[0]
                
                # Get paginated results
                query = f'''
                    SELECT id, query, language, response, response_time,
                           sources_count, cached, filters, timestamp
                    FROM query_history
                    WHERE {where_clause}
                    ORDER BY timestamp DESC
                    LIMIT ? OFFSET ?
                '''
                cursor.execute(query, params + [limit, offset])
                
                history = []
                for row in cursor.fetchall():
                    history.append({
                        'id': row[0],
                        'query': row[1],
                        'language': row[2],
                        'response': row[3],
                        'response_time': row[4],
                        'sources_count': row[5],
                        'cached': bool(row[6]),
                        'filters': row[7],
                        'timestamp': row[8]
                    })
                
                return {
                    'history': history,
                    'total': total,
                    'has_more': offset + limit < total,
                    'page': offset // limit + 1 if limit > 0 else 1,
                    'total_pages': (total + limit - 1) // limit if limit > 0 else 1
                }
                
        except Exception as e:
            logger.error(f"Error fetching query history: {e}")
            return {'history': [], 'total': 0, 'has_more': False}
    
    def log_activity(
        self,
        user_id: int,
        activity_type: str,
        details: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        """Log user activity"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO user_activity 
                    (user_id, activity_type, details, ip_address, user_agent)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, activity_type, details, ip_address, user_agent))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error logging activity: {e}")
            return False
    
    def get_user_stats(self, user_id: int, days: int = 30) -> Dict:
        """Get comprehensive user statistics"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                cutoff_date = datetime.now() - timedelta(days=days)
                
                # Total queries
                cursor.execute('''
                    SELECT COUNT(*) FROM query_history
                    WHERE user_id = ? AND timestamp >= ?
                ''', (user_id, cutoff_date))
                total_queries = cursor.fetchone()[0]
                
                # Average response time
                cursor.execute('''
                    SELECT AVG(response_time) FROM query_history
                    WHERE user_id = ? AND timestamp >= ?
                ''', (user_id, cutoff_date))
                avg_response_time = cursor.fetchone()[0] or 0
                
                # Cache hit rate
                cursor.execute('''
                    SELECT 
                        SUM(CASE WHEN cached = 1 THEN 1 ELSE 0 END) as cached_count,
                        COUNT(*) as total_count
                    FROM query_history
                    WHERE user_id = ? AND timestamp >= ?
                ''', (user_id, cutoff_date))
                row = cursor.fetchone()
                cache_hit_rate = (row[0] / row[1] * 100) if row[1] > 0 else 0
                
                # Most used language
                cursor.execute('''
                    SELECT language, COUNT(*) as count
                    FROM query_history
                    WHERE user_id = ? AND timestamp >= ?
                    GROUP BY language
                    ORDER BY count DESC
                    LIMIT 1
                ''', (user_id, cutoff_date))
                result = cursor.fetchone()
                most_used_language = result[0] if result else 'en'
                
                # Query frequency by day
                cursor.execute('''
                    SELECT DATE(timestamp) as date, COUNT(*) as count
                    FROM query_history
                    WHERE user_id = ? AND timestamp >= ?
                    GROUP BY DATE(timestamp)
                    ORDER BY date DESC
                ''', (user_id, cutoff_date))
                daily_activity = [{'date': row[0], 'count': row[1]} for row in cursor.fetchall()]
                
                # Popular queries
                cursor.execute('''
                    SELECT query, COUNT(*) as frequency
                    FROM query_history
                    WHERE user_id = ? AND timestamp >= ?
                    GROUP BY query
                    ORDER BY frequency DESC
                    LIMIT 5
                ''', (user_id, cutoff_date))
                popular_queries = [{'query': row[0], 'count': row[1]} for row in cursor.fetchall()]
                
                return {
                    'total_queries': total_queries,
                    'avg_response_time': round(avg_response_time, 2),
                    'cache_hit_rate': round(cache_hit_rate, 1),
                    'most_used_language': most_used_language,
                    'daily_activity': daily_activity,
                    'popular_queries': popular_queries,
                    'period_days': days
                }
                
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {}
    
    def save_favorite_query(
        self,
        user_id: int,
        query: str,
        title: Optional[str] = None,
        filters: Optional[Dict] = None
    ) -> int:
        """Save a query as favorite"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                filters_json = str(filters) if filters else None
                
                cursor.execute('''
                    INSERT INTO favorite_queries (user_id, query, title, filters)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, query, title or query[:50], filters_json))
                
                conn.commit()
                return cursor.lastrowid
                
        except Exception as e:
            logger.error(f"Error saving favorite query: {e}")
            return 0
    
    def get_favorite_queries(self, user_id: int) -> List[Dict]:
        """Get user's favorite queries"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, query, title, filters, created_at
                    FROM favorite_queries
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                ''', (user_id,))
                
                return [{
                    'id': row[0],
                    'query': row[1],
                    'title': row[2],
                    'filters': row[3],
                    'created_at': row[4]
                } for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error fetching favorite queries: {e}")
            return []
    
    def delete_query_from_history(self, query_id: int, user_id: int) -> bool:
        """Delete a specific query from history"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    DELETE FROM query_history
                    WHERE id = ? AND user_id = ?
                ''', (query_id, user_id))
                
                deleted = cursor.rowcount > 0
                conn.commit()
                return deleted
                
        except Exception as e:
            logger.error(f"Error deleting query: {e}")
            return False
    
    def clear_history(self, user_id: int, days: Optional[int] = None) -> int:
        """Clear user's query history"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                if days:
                    cutoff_date = datetime.now() - timedelta(days=days)
                    cursor.execute('''
                        DELETE FROM query_history
                        WHERE user_id = ? AND timestamp < ?
                    ''', (user_id, cutoff_date))
                else:
                    cursor.execute('''
                        DELETE FROM query_history WHERE user_id = ?
                    ''', (user_id,))
                
                deleted_count = cursor.rowcount
                conn.commit()
                return deleted_count
                
        except Exception as e:
            logger.error(f"Error clearing history: {e}")
            return 0
    
    def get_user_preferences(self, user_id: int) -> Dict:
        """Get user preferences"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT preferred_language, preferred_sectors, 
                           preferred_locations, notification_settings, theme
                    FROM user_preferences
                    WHERE user_id = ?
                ''', (user_id,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'preferred_language': row[0],
                        'preferred_sectors': row[1],
                        'preferred_locations': row[2],
                        'notification_settings': row[3],
                        'theme': row[4]
                    }
                else:
                    # Return defaults
                    return {
                        'preferred_language': 'en',
                        'preferred_sectors': None,
                        'preferred_locations': None,
                        'notification_settings': None,
                        'theme': 'light'
                    }
                    
        except Exception as e:
            logger.error(f"Error getting preferences: {e}")
            return {}
    
    def update_user_preferences(self, user_id: int, preferences: Dict) -> bool:
        """Update user preferences"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Check if preferences exist
                cursor.execute('SELECT user_id FROM user_preferences WHERE user_id = ?', (user_id,))
                exists = cursor.fetchone()
                
                if exists:
                    # Update
                    updates = []
                    params = []
                    
                    for key in ['preferred_language', 'preferred_sectors', 
                               'preferred_locations', 'notification_settings', 'theme']:
                        if key in preferences:
                            updates.append(f'{key} = ?')
                            params.append(preferences[key])
                    
                    if updates:
                        params.append(user_id)
                        query = f'''
                            UPDATE user_preferences 
                            SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP
                            WHERE user_id = ?
                        '''
                        cursor.execute(query, params)
                else:
                    # Insert
                    cursor.execute('''
                        INSERT INTO user_preferences 
                        (user_id, preferred_language, preferred_sectors, 
                         preferred_locations, notification_settings, theme)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (user_id,
                          preferences.get('preferred_language', 'en'),
                          preferences.get('preferred_sectors'),
                          preferences.get('preferred_locations'),
                          preferences.get('notification_settings'),
                          preferences.get('theme', 'light')))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error updating preferences: {e}")
            return False


# Create singleton instance
user_history_service = UserHistoryService()
