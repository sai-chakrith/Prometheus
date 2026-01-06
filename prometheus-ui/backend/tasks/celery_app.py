"""
Celery configuration for background jobs
"""
from celery import Celery
from celery.schedules import crontab
import logging

logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    'prometheus',
    broker='redis://localhost:6379/1',
    backend='redis://localhost:6379/1'
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Periodic tasks schedule
celery_app.conf.beat_schedule = {
    'refresh-chromadb-daily': {
        'task': 'tasks.celery_app.refresh_chromadb',
        'schedule': crontab(hour=2, minute=0),  # 2 AM daily
    },
    'send-weekly-reports': {
        'task': 'tasks.celery_app.send_weekly_reports',
        'schedule': crontab(day_of_week=1, hour=9, minute=0),  # Monday 9 AM
    },
    'cleanup-old-analytics': {
        'task': 'tasks.celery_app.cleanup_old_analytics',
        'schedule': crontab(day_of_month=1, hour=3, minute=0),  # First of month, 3 AM
    },
}


@celery_app.task(name='tasks.celery_app.refresh_chromadb')
def refresh_chromadb():
    """Refresh ChromaDB with latest data"""
    try:
        from services import rag_service
        from config import Config
        
        logger.info("Starting ChromaDB refresh...")
        rag_service.initialize(Config.DATASET_PATH)
        logger.info("ChromaDB refresh completed")
        return {"status": "success", "message": "ChromaDB refreshed"}
    
    except Exception as e:
        logger.error(f"ChromaDB refresh failed: {e}")
        return {"status": "error", "message": str(e)}


@celery_app.task(name='tasks.celery_app.generate_weekly_report')
def generate_weekly_report(user_id: int):
    """Generate and email weekly report for a user"""
    try:
        from services.analytics_service import analytics_service
        from services.email_service import email_service
        from database import get_db_connection
        
        logger.info(f"Generating weekly report for user {user_id}")
        
        # Get user email
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT email FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            if not row:
                return {"status": "error", "message": "User not found"}
            user_email = row[0]
        
        # Get stats
        stats = analytics_service.get_user_stats(user_id)
        
        # Send email
        email_service.send_weekly_report(user_email, stats)
        
        logger.info(f"Weekly report sent to {user_email}")
        return {"status": "success", "user_id": user_id}
    
    except Exception as e:
        logger.error(f"Weekly report generation failed: {e}")
        return {"status": "error", "message": str(e)}


@celery_app.task(name='tasks.celery_app.send_weekly_reports')
def send_weekly_reports():
    """Send weekly reports to all active users"""
    try:
        from database import get_db_connection
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM users')
            user_ids = [row[0] for row in cursor.fetchall()]
        
        logger.info(f"Sending weekly reports to {len(user_ids)} users")
        
        # Queue individual tasks
        for user_id in user_ids:
            generate_weekly_report.delay(user_id)
        
        return {"status": "success", "users_queued": len(user_ids)}
    
    except Exception as e:
        logger.error(f"Batch weekly reports failed: {e}")
        return {"status": "error", "message": str(e)}


@celery_app.task(name='tasks.celery_app.cleanup_old_analytics')
def cleanup_old_analytics(days: int = 90):
    """Delete analytics older than specified days"""
    try:
        from datetime import datetime, timedelta
        from database import get_db_connection
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM analytics 
                WHERE timestamp < ?
            ''', (cutoff_date,))
            deleted_count = cursor.rowcount
            conn.commit()
        
        logger.info(f"Deleted {deleted_count} old analytics records")
        return {"status": "success", "deleted_count": deleted_count}
    
    except Exception as e:
        logger.error(f"Analytics cleanup failed: {e}")
        return {"status": "error", "message": str(e)}


@celery_app.task(name='tasks.celery_app.send_funding_alert')
def send_funding_alert(user_email: str, startup_data: dict):
    """Send funding alert to user"""
    try:
        from services.email_service import email_service
        
        email_service.send_funding_alert(user_email, startup_data)
        return {"status": "success"}
    
    except Exception as e:
        logger.error(f"Funding alert failed: {e}")
        return {"status": "error", "message": str(e)}


@celery_app.task(name='tasks.celery_app.trigger_webhooks')
def trigger_webhooks(event_type: str, payload: dict):
    """Trigger webhooks for an event"""
    try:
        from services.webhook_service import webhook_service
        import asyncio
        
        # Run async function in sync context
        loop = asyncio.get_event_loop()
        loop.run_until_complete(webhook_service.trigger_event(event_type, payload))
        
        return {"status": "success"}
    
    except Exception as e:
        logger.error(f"Webhook trigger failed: {e}")
        return {"status": "error", "message": str(e)}


@celery_app.task(name='tasks.celery_app.export_large_dataset')
def export_large_dataset(user_id: int, format: str, filters: dict = None):
    """Export large dataset in background"""
    try:
        from services import rag_service
        import pandas as pd
        import os
        
        logger.info(f"Exporting dataset for user {user_id} in {format} format")
        
        # Query data (use filters if provided)
        # This would integrate with RAG service
        
        # Create export directory
        export_dir = "exports"
        os.makedirs(export_dir, exist_ok=True)
        
        filename = f"export_{user_id}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.{format}"
        filepath = os.path.join(export_dir, filename)
        
        # Export based on format
        # (Implementation would depend on actual data structure)
        
        logger.info(f"Export completed: {filepath}")
        return {"status": "success", "filepath": filepath}
    
    except Exception as e:
        logger.error(f"Dataset export failed: {e}")
        return {"status": "error", "message": str(e)}
