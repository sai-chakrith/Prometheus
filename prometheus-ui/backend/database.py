"""
Database models and authentication for Prometheus RAG
"""
import sqlite3
from datetime import datetime, timedelta
import secrets
from typing import Optional, Dict, List
from contextlib import contextmanager
import threading
import os
import bcrypt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_PATH = os.getenv("DATABASE_PATH", "prometheus.db")
SESSION_EXPIRY_DAYS = int(os.getenv("SESSION_EXPIRY_DAYS", "30"))

# Thread-local storage for database connections (connection pooling)
_thread_local = threading.local()

@contextmanager
def get_db_connection():
    """Context manager for database connections with connection pooling"""
    if not hasattr(_thread_local, 'conn') or _thread_local.conn is None:
        _thread_local.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        _thread_local.conn.row_factory = sqlite3.Row
    try:
        yield _thread_local.conn
    except Exception as e:
        _thread_local.conn.rollback()
        raise

def init_database():
    """Initialize SQLite database with users and chat_history tables"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # Chat history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            query TEXT NOT NULL,
            language TEXT NOT NULL,
            response TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Create indexes for better query performance
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_chat_history_user_id 
        ON chat_history(user_id)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_chat_history_timestamp 
        ON chat_history(timestamp DESC)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_chat_history_user_timestamp 
        ON chat_history(user_id, timestamp DESC)
    ''')
    
    # Session tokens table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    print("Database initialized successfully")

def hash_password(password: str) -> str:
    """Hash password using bcrypt (secure password hashing)"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against bcrypt hash"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False

def validate_password_strength(password: str) -> tuple[bool, str]:
    """Validate password meets security requirements"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    return True, "Password is strong"

def generate_token() -> str:
    """Generate secure session token"""
    return secrets.token_urlsafe(32)

def create_user(username: str, email: str, password: str) -> Dict:
    """Create new user account with validation"""
    # Validate inputs
    if not username or len(username) < 3:
        return {'success': False, 'error': 'Username must be at least 3 characters long'}
    if not email or '@' not in email:
        return {'success': False, 'error': 'Invalid email address'}
    
    # Validate password strength
    is_valid, message = validate_password_strength(password)
    if not is_valid:
        return {'success': False, 'error': message}
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            password_hash = hash_password(password)
            cursor.execute(
                'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                (username.strip(), email.strip().lower(), password_hash)
            )
            conn.commit()
            user_id = cursor.lastrowid
            
            return {
                'success': True,
                'user_id': user_id,
                'username': username.strip(),
                'email': email.strip().lower()
            }
    except sqlite3.IntegrityError as e:
        if 'username' in str(e):
            return {'success': False, 'error': 'Username already exists'}
        elif 'email' in str(e):
            return {'success': False, 'error': 'Email already exists'}
        return {'success': False, 'error': 'Registration failed'}
    except Exception as e:
        return {'success': False, 'error': f'An error occurred: {str(e)}'}

def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """Authenticate user and create session using bcrypt"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Fetch user by username
            cursor.execute(
                'SELECT id, username, email, password_hash FROM users WHERE username = ?',
                (username.strip(),)
            )
            
            user = cursor.fetchone()
            if not user:
                return None
            
            user_id, username, email, stored_hash = user
            
            # Verify password using bcrypt
            if not verify_password(password, stored_hash):
                return None
            
            # Update last login
            cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', (datetime.now(), user_id))
            
            # Clean up expired sessions
            cursor.execute('DELETE FROM sessions WHERE expires_at < ?', (datetime.now(),))
            
            # Create session token
            token = generate_token()
            expires_at = datetime.now() + timedelta(days=SESSION_EXPIRY_DAYS)
            cursor.execute(
                'INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?)',
                (user_id, token, expires_at)
            )
            
            conn.commit()
            
            return {
                'user_id': user_id,
                'username': username,
                'email': email,
                'token': token
            }
    except Exception as e:
        print(f"Authentication error: {e}")
        return None

def verify_token(token: str) -> Optional[Dict]:
    """Verify session token and return user info"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT users.id, users.username, users.email, sessions.expires_at
                FROM sessions
                JOIN users ON sessions.user_id = users.id
                WHERE sessions.token = ?
            ''', (token,))
            
            result = cursor.fetchone()
            
            if not result:
                return None
            
            user_id, username, email, expires_at = result
            
            # Check if token expired
            if datetime.fromisoformat(expires_at) < datetime.now():
                return None
            
            return {
                'user_id': user_id,
                'username': username,
                'email': email
            }
    except Exception as e:
        print(f"Token verification error: {e}")
        return None

def save_chat(user_id: int, query: str, language: str, response: str):
    """Save chat interaction to history"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute(
                'INSERT INTO chat_history (user_id, query, language, response) VALUES (?, ?, ?, ?)',
                (user_id, query, language, response)
            )
            
            conn.commit()
    except Exception as e:
        print(f"Error saving chat: {e}")

def get_chat_history(
    user_id: int, 
    limit: int = 50, 
    offset: int = 0,
    language: Optional[str] = None,
    search: Optional[str] = None
) -> Dict:
    """
    Retrieve user's chat history with pagination, filtering, and search
    
    Args:
        user_id: User ID
        limit: Number of records per page (default 50)
        offset: Offset for pagination
        language: Filter by language code (optional)
        search: Search in query text (optional)
    
    Returns:
        Dict with 'chats', 'total', 'has_more' keys
    """
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
            
            where_clause = ' AND '.join(where_clauses)
            
            # Get total count
            count_query = f'SELECT COUNT(*) FROM chat_history WHERE {where_clause}'
            cursor.execute(count_query, params)
            total = cursor.fetchone()[0]
            
            # Get paginated results
            query = f'''
                SELECT id, query, language, response, timestamp
                FROM chat_history
                WHERE {where_clause}
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
            '''
            cursor.execute(query, params + [limit, offset])
            
            history = []
            for row in cursor.fetchall():
                # Truncate long responses for list view (optimize transfer size)
                response_preview = row[3][:200] + '...' if len(row[3]) > 200 else row[3]
                
                history.append({
                    'id': row[0],
                    'query': row[1],
                    'language': row[2],
                    'response': row[3],  # Full response
                    'response_preview': response_preview,  # Short preview
                    'timestamp': row[4]
                })
        
            return {
                'chats': history,
                'total': total,
                'has_more': offset + limit < total,
                'page': offset // limit + 1 if limit > 0 else 1,
                'total_pages': (total + limit - 1) // limit if limit > 0 else 1
            }
    except Exception as e:
        print(f"Error fetching chat history: {e}")
        return {
            'chats': [],
            'total': 0,
            'has_more': False,
            'page': 1,
            'total_pages': 0
        }

def logout_user(token: str):
    """Remove session token"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM sessions WHERE token = ?', (token,))
            conn.commit()
    except Exception as e:
        print(f"Error logging out user: {e}")


def delete_chat(chat_id: int, user_id: int) -> bool:
    """
    Delete a specific chat from history
    
    Args:
        chat_id: Chat ID to delete
        user_id: User ID (for security - ensure user owns the chat)
    
    Returns:
        True if deleted, False if not found or unauthorized
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM chat_history
                WHERE id = ? AND user_id = ?
            ''', (chat_id, user_id))
            
            deleted = cursor.rowcount > 0
            conn.commit()
            
            return deleted
    except Exception as e:
        print(f"Error deleting chat: {e}")
        return False


def clear_chat_history(user_id: int) -> int:
    """
    Clear all chat history for a user
    
    Args:
        user_id: User ID
    
    Returns:
        Number of chats deleted
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM chat_history WHERE user_id = ?', (user_id,))
            deleted_count = cursor.rowcount
            
            conn.commit()
            
            return deleted_count
    except Exception as e:
        print(f"Error clearing chat history: {e}")
        return 0
    
    return deleted_count


# Initialize database on module import
init_database()
