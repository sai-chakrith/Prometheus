"""
Performance optimization utilities for Prometheus
Includes batch processing, pagination, and query optimization
"""
import time
import logging
from typing import List, Dict, Any, Optional, TypeVar, Generic
from dataclasses import dataclass
from functools import wraps
import asyncio

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class PaginationParams:
    """Pagination parameters"""
    page: int = 1
    page_size: int = 20
    
    @property
    def offset(self) -> int:
        """Calculate offset for database query"""
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        """Get limit for database query"""
        return self.page_size
    
    def validate(self):
        """Validate pagination parameters"""
        if self.page < 1:
            raise ValueError("Page must be >= 1")
        if self.page_size < 1 or self.page_size > 100:
            raise ValueError("Page size must be between 1 and 100")


@dataclass
class PaginatedResponse(Generic[T]):
    """Paginated response wrapper"""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    @classmethod
    def create(cls, items: List[T], total: int, pagination: PaginationParams):
        """Create paginated response"""
        total_pages = (total + pagination.page_size - 1) // pagination.page_size
        return cls(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=total_pages
        )


class BatchProcessor:
    """Process items in batches to avoid memory issues"""
    
    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size
    
    def process(self, items: List[T], processor: callable) -> List[Any]:
        """
        Process items in batches
        
        Args:
            items: List of items to process
            processor: Function to process each batch
        
        Returns:
            List of processed results
        """
        results = []
        total_batches = (len(items) + self.batch_size - 1) // self.batch_size
        
        for i in range(0, len(items), self.batch_size):
            batch_num = i // self.batch_size + 1
            batch = items[i:i + self.batch_size]
            
            logger.debug(f"Processing batch {batch_num}/{total_batches}")
            
            try:
                batch_results = processor(batch)
                results.extend(batch_results)
            except Exception as e:
                logger.error(f"Error processing batch {batch_num}: {e}")
                raise
        
        return results
    
    async def process_async(self, items: List[T], processor: callable) -> List[Any]:
        """
        Process items in batches asynchronously
        
        Args:
            items: List of items to process
            processor: Async function to process each batch
        
        Returns:
            List of processed results
        """
        results = []
        total_batches = (len(items) + self.batch_size - 1) // self.batch_size
        
        for i in range(0, len(items), self.batch_size):
            batch_num = i // self.batch_size + 1
            batch = items[i:i + self.batch_size]
            
            logger.debug(f"Processing batch {batch_num}/{total_batches}")
            
            try:
                batch_results = await processor(batch)
                results.extend(batch_results)
            except Exception as e:
                logger.error(f"Error processing batch {batch_num}: {e}")
                raise
        
        return results


class PerformanceMonitor:
    """Monitor and log performance metrics"""
    
    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}
    
    def record(self, metric_name: str, value: float):
        """Record a metric value"""
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        self.metrics[metric_name].append(value)
    
    def get_stats(self, metric_name: str) -> Dict[str, float]:
        """Get statistics for a metric"""
        if metric_name not in self.metrics or not self.metrics[metric_name]:
            return {}
        
        values = self.metrics[metric_name]
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "total": sum(values)
        }
    
    def clear(self):
        """Clear all metrics"""
        self.metrics.clear()


# Global performance monitor
perf_monitor = PerformanceMonitor()


def measure_performance(metric_name: str):
    """
    Decorator to measure function execution time
    
    Usage:
        @measure_performance("query_processing")
        def process_query(query):
            # ... processing logic
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                elapsed = time.time() - start_time
                perf_monitor.record(metric_name, elapsed)
                logger.debug(f"{metric_name}: {elapsed:.3f}s")
        return wrapper
    return decorator


def measure_async_performance(metric_name: str):
    """
    Decorator to measure async function execution time
    
    Usage:
        @measure_async_performance("async_query")
        async def process_query(query):
            # ... async processing logic
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                elapsed = time.time() - start_time
                perf_monitor.record(metric_name, elapsed)
                logger.debug(f"{metric_name}: {elapsed:.3f}s")
        return wrapper
    return decorator


class QueryOptimizer:
    """Optimize database queries"""
    
    @staticmethod
    def build_where_clause(filters: Dict[str, Any]) -> tuple[str, List[Any]]:
        """
        Build SQL WHERE clause from filters
        
        Args:
            filters: Dictionary of column: value pairs
        
        Returns:
            Tuple of (where_clause, parameters)
        """
        if not filters:
            return "", []
        
        conditions = []
        params = []
        
        for column, value in filters.items():
            if value is None:
                conditions.append(f"{column} IS NULL")
            elif isinstance(value, (list, tuple)):
                placeholders = ','.join(['?' for _ in value])
                conditions.append(f"{column} IN ({placeholders})")
                params.extend(value)
            else:
                conditions.append(f"{column} = ?")
                params.append(value)
        
        where_clause = " AND ".join(conditions)
        return f"WHERE {where_clause}", params
    
    @staticmethod
    def build_pagination_clause(pagination: PaginationParams) -> str:
        """Build LIMIT and OFFSET clause"""
        return f"LIMIT {pagination.limit} OFFSET {pagination.offset}"


class CacheWarmer:
    """Pre-warm caches with frequently accessed data"""
    
    def __init__(self, cache_service):
        self.cache_service = cache_service
        self.warmup_queries = []
    
    def register_warmup_query(self, key: str, query: str):
        """Register a query to run during warmup"""
        self.warmup_queries.append((key, query))
    
    async def warmup(self):
        """Execute all warmup queries"""
        logger.info(f"Starting cache warmup with {len(self.warmup_queries)} queries")
        
        for key, query in self.warmup_queries:
            try:
                # Execute query and cache result
                # This is a placeholder - implement based on your cache service
                logger.debug(f"Warming up cache for: {key}")
                # result = await execute_query(query)
                # self.cache_service.set(key, result)
            except Exception as e:
                logger.warning(f"Failed to warmup cache for {key}: {e}")
        
        logger.info("Cache warmup completed")


class ConnectionPool:
    """Simple connection pooling for database connections"""
    
    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self.pool = []
        self.in_use = set()
    
    def get_connection(self):
        """Get a connection from pool"""
        if self.pool:
            conn = self.pool.pop()
        elif len(self.in_use) < self.max_connections:
            # Create new connection
            conn = self._create_connection()
        else:
            raise RuntimeError("Connection pool exhausted")
        
        self.in_use.add(conn)
        return conn
    
    def return_connection(self, conn):
        """Return connection to pool"""
        if conn in self.in_use:
            self.in_use.remove(conn)
            self.pool.append(conn)
    
    def _create_connection(self):
        """Create new database connection"""
        # Implement based on your database
        raise NotImplementedError
    
    def close_all(self):
        """Close all connections"""
        for conn in self.pool:
            conn.close()
        for conn in self.in_use:
            conn.close()
        self.pool.clear()
        self.in_use.clear()


def optimize_chroma_query(
    query_text: str,
    n_results: int = 10,
    max_results: int = 100
) -> Dict[str, Any]:
    """
    Optimize ChromaDB query parameters
    
    Args:
        query_text: Query text
        n_results: Number of results to retrieve
        max_results: Maximum allowed results
    
    Returns:
        Optimized query parameters
    """
    # Limit results to prevent performance issues
    n_results = min(n_results, max_results)
    
    # Adjust based on query complexity
    if len(query_text) > 200:
        # Complex query, get more results for better reranking
        n_results = min(n_results * 2, max_results)
    
    return {
        "n_results": n_results,
        "include": ["documents", "metadatas", "distances"]
    }


def batch_write_to_disk(
    data_buffer: List[Any],
    write_func: callable,
    batch_size: int = 10
) -> bool:
    """
    Batch write data to disk instead of writing on every change
    
    Args:
        data_buffer: Buffer of data to write
        write_func: Function to perform actual write
        batch_size: Write after this many items
    
    Returns:
        True if write was performed
    """
    if len(data_buffer) >= batch_size:
        try:
            write_func(data_buffer)
            data_buffer.clear()
            return True
        except Exception as e:
            logger.error(f"Batch write failed: {e}")
            return False
    return False
