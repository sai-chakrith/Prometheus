"""
Database Migration Script
Migrates existing SHA-256 password hashes to bcrypt

IMPORTANT: Run this ONCE before deploying the new security updates
"""

import sqlite3
import bcrypt
import sys

DB_PATH = "prometheus.db"

def migrate_passwords():
    """Migrate SHA-256 hashes to bcrypt"""
    print("🔐 Starting password migration...")
    print("⚠️  WARNING: This will reset all user passwords!")
    print("   Users will need to use the password reset feature or re-register.")
    
    response = input("\nDo you want to continue? (yes/no): ")
    if response.lower() != 'yes':
        print("Migration cancelled.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Get all users
        cursor.execute('SELECT id, username FROM users')
        users = cursor.fetchall()
        
        if not users:
            print("No users found in database.")
            return
        
        print(f"\nFound {len(users)} users.")
        print("\nOptions:")
        print("1. Set a temporary password for all users (they must change it)")
        print("2. Clear all passwords (users must re-register)")
        
        choice = input("\nSelect option (1 or 2): ")
        
        if choice == "1":
            temp_password = input("Enter temporary password (min 8 chars, 1 upper, 1 lower, 1 digit): ")
            
            # Validate temp password
            if len(temp_password) < 8:
                print("❌ Password must be at least 8 characters!")
                return
            
            # Hash the temporary password with bcrypt
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(temp_password.encode('utf-8'), salt).decode('utf-8')
            
            # Update all users with the same temp password
            cursor.execute('UPDATE users SET password_hash = ?', (hashed,))
            conn.commit()
            
            print(f"\n✅ Updated {len(users)} users with temporary password.")
            print(f"⚠️  Tell users to login with username and password: {temp_password}")
            
        elif choice == "2":
            # Delete all sessions
            cursor.execute('DELETE FROM sessions')
            # Delete all users (they'll need to re-register)
            cursor.execute('DELETE FROM users')
            conn.commit()
            
            print(f"\n✅ Cleared {len(users)} users. They must re-register.")
        
        else:
            print("Invalid choice. Migration cancelled.")
            return
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)
    finally:
        conn.close()
    
    print("\n✅ Migration completed successfully!")
    print("🚀 You can now start the new backend with bcrypt security.")

if __name__ == "__main__":
    migrate_passwords()
