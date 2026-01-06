"""
Database migration management system for Prometheus
Tracks schema versions and applies migrations sequentially
"""
import sqlite3
import os
import logging
from datetime import datetime
from typing import List, Tuple, Callable
from pathlib import Path

logger = logging.getLogger(__name__)


class Migration:
    """Represents a single database migration"""
    
    def __init__(self, version: int, name: str, up: Callable, down: Callable):
        self.version = version
        self.name = name
        self.up = up  # Function to apply migration
        self.down = down  # Function to rollback migration
    
    def __repr__(self):
        return f"Migration(v{self.version}: {self.name})"


class MigrationManager:
    """Manages database schema migrations"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.migrations: List[Migration] = []
        self._init_migration_table()
    
    def _init_migration_table(self):
        """Create migrations tracking table if not exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("Migration tracking table initialized")
    
    def register_migration(self, version: int, name: str, up: Callable, down: Callable):
        """Register a new migration"""
        migration = Migration(version, name, up, down)
        self.migrations.append(migration)
        logger.debug(f"Registered {migration}")
    
    def get_current_version(self) -> int:
        """Get current schema version"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT MAX(version) FROM schema_migrations")
        result = cursor.fetchone()
        conn.close()
        
        current_version = result[0] if result[0] is not None else 0
        return current_version
    
    def get_applied_migrations(self) -> List[int]:
        """Get list of applied migration versions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT version FROM schema_migrations ORDER BY version")
        versions = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return versions
    
    def migrate(self, target_version: int = None):
        """
        Apply pending migrations up to target version
        If target_version is None, apply all pending migrations
        """
        current_version = self.get_current_version()
        applied_versions = set(self.get_applied_migrations())
        
        # Sort migrations by version
        sorted_migrations = sorted(self.migrations, key=lambda m: m.version)
        
        # Determine target version
        if target_version is None:
            target_version = sorted_migrations[-1].version if sorted_migrations else 0
        
        logger.info(f"Current version: {current_version}")
        logger.info(f"Target version: {target_version}")
        
        # Apply pending migrations
        for migration in sorted_migrations:
            if migration.version > target_version:
                break
            
            if migration.version in applied_versions:
                logger.debug(f"Skipping already applied {migration}")
                continue
            
            logger.info(f"Applying {migration}")
            
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Apply migration
                migration.up(cursor)
                
                # Record migration
                cursor.execute(
                    "INSERT INTO schema_migrations (version, name) VALUES (?, ?)",
                    (migration.version, migration.name)
                )
                
                conn.commit()
                conn.close()
                
                logger.info(f"✅ Applied {migration}")
                
            except Exception as e:
                logger.error(f"❌ Failed to apply {migration}: {str(e)}")
                conn.rollback()
                conn.close()
                raise
    
    def rollback(self, target_version: int):
        """Rollback to a specific version"""
        current_version = self.get_current_version()
        applied_versions = sorted(self.get_applied_migrations(), reverse=True)
        
        logger.info(f"Rolling back from version {current_version} to {target_version}")
        
        # Sort migrations in reverse order
        sorted_migrations = sorted(self.migrations, key=lambda m: m.version, reverse=True)
        
        for migration in sorted_migrations:
            if migration.version <= target_version:
                break
            
            if migration.version not in applied_versions:
                logger.debug(f"Skipping not applied {migration}")
                continue
            
            logger.info(f"Rolling back {migration}")
            
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Rollback migration
                migration.down(cursor)
                
                # Remove migration record
                cursor.execute(
                    "DELETE FROM schema_migrations WHERE version = ?",
                    (migration.version,)
                )
                
                conn.commit()
                conn.close()
                
                logger.info(f"✅ Rolled back {migration}")
                
            except Exception as e:
                logger.error(f"❌ Failed to rollback {migration}: {str(e)}")
                conn.rollback()
                conn.close()
                raise
    
    def status(self):
        """Print migration status"""
        current_version = self.get_current_version()
        applied_versions = set(self.get_applied_migrations())
        
        print(f"\n{'='*60}")
        print(f"Database: {self.db_path}")
        print(f"Current Version: {current_version}")
        print(f"{'='*60}\n")
        
        sorted_migrations = sorted(self.migrations, key=lambda m: m.version)
        
        for migration in sorted_migrations:
            status = "✅ Applied" if migration.version in applied_versions else "⏳ Pending"
            print(f"  {status} - v{migration.version:03d}: {migration.name}")
        
        print(f"\n{'='*60}\n")


# Example migrations for Prometheus
def create_migration_manager(db_path: str) -> MigrationManager:
    """Create and configure migration manager with all migrations"""
    manager = MigrationManager(db_path)
    
    # Migration 001: Initial schema
    def migration_001_up(cursor):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_id INTEGER,
                query TEXT NOT NULL,
                response TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
    
    def migration_001_down(cursor):
        cursor.execute("DROP TABLE IF EXISTS chat_history")
        cursor.execute("DROP TABLE IF EXISTS users")
    
    manager.register_migration(1, "initial_schema", migration_001_up, migration_001_down)
    
    # Migration 002: Add feedback table
    def migration_002_up(cursor):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                query TEXT NOT NULL,
                response TEXT NOT NULL,
                rating INTEGER CHECK(rating BETWEEN 1 AND 5),
                comment TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
    
    def migration_002_down(cursor):
        cursor.execute("DROP TABLE IF EXISTS feedback")
    
    manager.register_migration(2, "add_feedback_table", migration_002_up, migration_002_down)
    
    # Migration 003: Add analytics table
    def migration_003_up(cursor):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                user_id INTEGER,
                session_id TEXT,
                metadata TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_analytics_event ON analytics(event_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_analytics_timestamp ON analytics(timestamp)")
    
    def migration_003_down(cursor):
        cursor.execute("DROP INDEX IF EXISTS idx_analytics_timestamp")
        cursor.execute("DROP INDEX IF EXISTS idx_analytics_event")
        cursor.execute("DROP TABLE IF EXISTS analytics")
    
    manager.register_migration(3, "add_analytics_table", migration_003_up, migration_003_down)
    
    # Migration 004: Add soft delete support
    def migration_004_up(cursor):
        cursor.execute("ALTER TABLE users ADD COLUMN deleted_at TIMESTAMP")
        cursor.execute("ALTER TABLE chat_history ADD COLUMN deleted_at TIMESTAMP")
        cursor.execute("ALTER TABLE feedback ADD COLUMN deleted_at TIMESTAMP")
    
    def migration_004_down(cursor):
        # SQLite doesn't support DROP COLUMN, so we'd need to recreate tables
        # For safety, we'll just log a warning
        logger.warning("Rollback of soft delete columns requires table recreation")
    
    manager.register_migration(4, "add_soft_delete", migration_004_up, migration_004_down)
    
    return manager


if __name__ == "__main__":
    # Command line interface for migrations
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python migrations.py <command> [args]")
        print("Commands:")
        print("  status                 - Show migration status")
        print("  migrate [version]      - Apply migrations (optionally to specific version)")
        print("  rollback <version>     - Rollback to specific version")
        sys.exit(1)
    
    command = sys.argv[1]
    db_path = os.getenv("DATABASE_PATH", "prometheus.db")
    
    manager = create_migration_manager(db_path)
    
    if command == "status":
        manager.status()
    elif command == "migrate":
        target = int(sys.argv[2]) if len(sys.argv) > 2 else None
        manager.migrate(target)
        manager.status()
    elif command == "rollback":
        if len(sys.argv) < 3:
            print("Error: rollback requires target version")
            sys.exit(1)
        target = int(sys.argv[2])
        manager.rollback(target)
        manager.status()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
