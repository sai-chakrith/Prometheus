"""
User Feedback System for continuous improvement
Collect thumbs up/down on responses to improve quality
"""
import sqlite3
from datetime import datetime
from typing import Optional

DB_PATH = "prometheus.db"

def init_feedback_table():
    """Add feedback table to database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            user_id INTEGER,
            rating INTEGER CHECK(rating IN (1, -1)),  -- 1 = thumbs up, -1 = thumbs down
            comment TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (chat_id) REFERENCES chat_history(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Feedback table initialized")

def save_feedback(
    chat_id: int,
    user_id: int,
    rating: int,  # 1 or -1
    comment: Optional[str] = None
):
    """Save user feedback on a response"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        'INSERT INTO feedback (chat_id, user_id, rating, comment) VALUES (?, ?, ?, ?)',
        (chat_id, user_id, rating, comment)
    )
    
    conn.commit()
    conn.close()

def get_feedback_stats():
    """Get overall feedback statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN rating = 1 THEN 1 ELSE 0 END) as thumbs_up,
            SUM(CASE WHEN rating = -1 THEN 1 ELSE 0 END) as thumbs_down,
            AVG(CASE WHEN rating = 1 THEN 1.0 ELSE 0.0 END) as satisfaction_rate
        FROM feedback
    ''')
    
    stats = cursor.fetchone()
    conn.close()
    
    return {
        'total': stats[0],
        'thumbs_up': stats[1],
        'thumbs_down': stats[2],
        'satisfaction_rate': stats[3]
    }

def get_low_rated_queries():
    """Get queries with thumbs down to improve"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT ch.query, ch.response, f.comment, f.timestamp
        FROM feedback f
        JOIN chat_history ch ON f.chat_id = ch.id
        WHERE f.rating = -1
        ORDER BY f.timestamp DESC
        LIMIT 20
    ''')
    
    results = cursor.fetchall()
    conn.close()
    
    return [
        {
            'query': row[0],
            'response': row[1],
            'comment': row[2],
            'timestamp': row[3]
        }
        for row in results
    ]

# FastAPI endpoints to add:
"""
@app.post("/api/feedback")
async def submit_feedback(
    chat_id: int,
    rating: int,
    comment: Optional[str] = None,
    authorization: str = Header(None)
):
    user = db.verify_token(authorization.replace("Bearer ", ""))
    if user:
        save_feedback(chat_id, user['user_id'], rating, comment)
        return {"success": True}
    return {"success": False}

@app.get("/api/feedback/stats")
async def feedback_stats():
    return get_feedback_stats()
"""

# Frontend (Chat.jsx) - Add thumbs up/down buttons:
"""
<div className="flex gap-2 mt-2">
    <button onClick={() => submitFeedback(chatId, 1)}>
        👍 Helpful
    </button>
    <button onClick={() => submitFeedback(chatId, -1)}>
        👎 Not Helpful
    </button>
</div>
"""

init_feedback_table()
