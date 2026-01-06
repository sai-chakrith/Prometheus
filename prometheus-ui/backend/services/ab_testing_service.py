"""
A/B Testing Service - Experiment framework
"""
import logging
import hashlib
from typing import Dict, Optional, List
from datetime import datetime
from database import get_db_connection

logger = logging.getLogger(__name__)


def init_ab_testing_tables():
    """Initialize A/B testing tables"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Experiments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS experiments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                variants TEXT NOT NULL,
                active BOOLEAN DEFAULT 1,
                start_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                end_date DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Assignments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS experiment_assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id INTEGER,
                user_id INTEGER,
                variant TEXT NOT NULL,
                assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (experiment_id) REFERENCES experiments (id),
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(experiment_id, user_id)
            )
        ''')
        
        # Metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS experiment_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id INTEGER,
                user_id INTEGER,
                variant TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (experiment_id) REFERENCES experiments (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        logger.info("A/B testing tables initialized")


class ABTestingService:
    """Service for A/B testing and experimentation"""
    
    def create_experiment(self, name: str, variants: List[str], description: str = None) -> int:
        """
        Create a new experiment
        
        Args:
            name: Experiment name
            variants: List of variant names (e.g., ['A', 'B'] or ['control', 'treatment'])
            description: Optional description
        
        Returns:
            Experiment ID
        """
        try:
            import json
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO experiments (name, description, variants)
                    VALUES (?, ?, ?)
                ''', (name, description, json.dumps(variants)))
                conn.commit()
                
                experiment_id = cursor.lastrowid
                logger.info(f"Created experiment '{name}' (ID: {experiment_id}) with variants: {variants}")
                return experiment_id
        
        except Exception as e:
            logger.error(f"Error creating experiment: {e}")
            raise
    
    def get_variant(self, experiment_name: str, user_id: int) -> str:
        """
        Get assigned variant for user in experiment
        
        Uses consistent hashing for stable assignments
        
        Args:
            experiment_name: Experiment name
            user_id: User ID
        
        Returns:
            Variant name
        """
        try:
            import json
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Get experiment
                cursor.execute('''
                    SELECT id, variants FROM experiments 
                    WHERE name = ? AND active = 1
                ''', (experiment_name,))
                
                row = cursor.fetchone()
                if not row:
                    logger.warning(f"Experiment '{experiment_name}' not found or inactive")
                    return "control"  # Default variant
                
                experiment_id, variants_json = row
                variants = json.loads(variants_json)
                
                # Check if user already assigned
                cursor.execute('''
                    SELECT variant FROM experiment_assignments
                    WHERE experiment_id = ? AND user_id = ?
                ''', (experiment_id, user_id))
                
                existing = cursor.fetchone()
                if existing:
                    return existing[0]
                
                # Assign using consistent hashing
                variant = self._assign_variant(user_id, variants)
                
                # Store assignment
                cursor.execute('''
                    INSERT INTO experiment_assignments (experiment_id, user_id, variant)
                    VALUES (?, ?, ?)
                ''', (experiment_id, user_id, variant))
                conn.commit()
                
                logger.debug(f"Assigned user {user_id} to variant '{variant}' in experiment '{experiment_name}'")
                return variant
        
        except Exception as e:
            logger.error(f"Error getting variant: {e}")
            return "control"
    
    def _assign_variant(self, user_id: int, variants: List[str]) -> str:
        """
        Assign variant using consistent hashing
        
        Same user always gets same variant
        """
        # Hash user_id to get consistent assignment
        hash_value = int(hashlib.md5(str(user_id).encode()).hexdigest(), 16)
        variant_index = hash_value % len(variants)
        return variants[variant_index]
    
    def track_metric(self, experiment_name: str, user_id: int, metric_name: str, 
                    metric_value: float):
        """
        Track a metric for user in experiment
        
        Args:
            experiment_name: Experiment name
            user_id: User ID
            metric_name: Metric name (e.g., 'response_time', 'conversion', 'satisfaction')
            metric_value: Metric value
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Get experiment ID and user's variant
                cursor.execute('''
                    SELECT e.id, ea.variant
                    FROM experiments e
                    JOIN experiment_assignments ea ON e.id = ea.experiment_id
                    WHERE e.name = ? AND ea.user_id = ?
                ''', (experiment_name, user_id))
                
                row = cursor.fetchone()
                if not row:
                    return
                
                experiment_id, variant = row
                
                # Store metric
                cursor.execute('''
                    INSERT INTO experiment_metrics 
                    (experiment_id, user_id, variant, metric_name, metric_value)
                    VALUES (?, ?, ?, ?, ?)
                ''', (experiment_id, user_id, variant, metric_name, metric_value))
                conn.commit()
                
                logger.debug(f"Tracked metric '{metric_name}' = {metric_value} for user {user_id}, variant '{variant}'")
        
        except Exception as e:
            logger.error(f"Error tracking metric: {e}")
    
    def get_experiment_results(self, experiment_name: str) -> Dict:
        """
        Get experiment results with statistical analysis
        
        Args:
            experiment_name: Experiment name
        
        Returns:
            Dict with results per variant
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Get experiment ID
                cursor.execute('''
                    SELECT id FROM experiments WHERE name = ?
                ''', (experiment_name,))
                
                row = cursor.fetchone()
                if not row:
                    return {}
                
                experiment_id = row[0]
                
                # Get metrics per variant
                cursor.execute('''
                    SELECT 
                        variant,
                        metric_name,
                        COUNT(*) as sample_size,
                        AVG(metric_value) as mean,
                        MIN(metric_value) as min,
                        MAX(metric_value) as max
                    FROM experiment_metrics
                    WHERE experiment_id = ?
                    GROUP BY variant, metric_name
                ''', (experiment_id,))
                
                results = {}
                for row in cursor.fetchall():
                    variant, metric_name, sample_size, mean, min_val, max_val = row
                    
                    if variant not in results:
                        results[variant] = {}
                    
                    results[variant][metric_name] = {
                        "sample_size": sample_size,
                        "mean": round(mean, 4) if mean else 0,
                        "min": round(min_val, 4) if min_val else 0,
                        "max": round(max_val, 4) if max_val else 0
                    }
                
                return results
        
        except Exception as e:
            logger.error(f"Error getting experiment results: {e}")
            return {}
    
    def stop_experiment(self, experiment_name: str):
        """Stop an active experiment"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE experiments 
                    SET active = 0, end_date = ?
                    WHERE name = ?
                ''', (datetime.now(), experiment_name))
                conn.commit()
                
                logger.info(f"Stopped experiment '{experiment_name}'")
        
        except Exception as e:
            logger.error(f"Error stopping experiment: {e}")
    
    def get_active_experiments(self) -> List[Dict]:
        """Get list of active experiments"""
        try:
            import json
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, name, description, variants, start_date
                    FROM experiments
                    WHERE active = 1
                ''')
                
                return [
                    {
                        "id": row[0],
                        "name": row[1],
                        "description": row[2],
                        "variants": json.loads(row[3]),
                        "start_date": row[4]
                    }
                    for row in cursor.fetchall()
                ]
        
        except Exception as e:
            logger.error(f"Error getting active experiments: {e}")
            return []


# Global A/B testing service instance
ab_testing_service = ABTestingService()


# Initialize tables on import
try:
    init_ab_testing_tables()
except Exception as e:
    logger.error(f"Failed to initialize A/B testing tables: {e}")
