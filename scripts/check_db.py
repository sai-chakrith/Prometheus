import sqlite3

conn = sqlite3.connect('prometheus.db')
cursor = conn.cursor()

# Get all tables
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = [row[0] for row in cursor.fetchall()]
print(f"📊 Database Tables: {tables}")

# Get chat history count
cursor.execute('SELECT COUNT(*) FROM chat_history')
chat_count = cursor.fetchone()[0]
print(f"💬 Chat History Records: {chat_count}")

# Get users count
cursor.execute('SELECT COUNT(*) FROM users')
user_count = cursor.fetchone()[0]
print(f"👥 Users: {user_count}")

# Get sessions count
cursor.execute('SELECT COUNT(*) FROM sessions')
session_count = cursor.fetchone()[0]
print(f"🔑 Active Sessions: {session_count}")

# Show sample chat history
if chat_count > 0:
    cursor.execute('''
        SELECT ch.query, ch.language, ch.timestamp, u.username 
        FROM chat_history ch 
        JOIN users u ON ch.user_id = u.id 
        ORDER BY ch.timestamp DESC 
        LIMIT 5
    ''')
    print(f"\n📝 Recent Chat History:")
    for row in cursor.fetchall():
        print(f"  - {row[3]}: {row[0][:50]}... ({row[1]}) at {row[2]}")

conn.close()
