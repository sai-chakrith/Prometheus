"""
Cache Service - Redis caching for query performance
"""
import logging
import json
from typing import Optional
import hashlib

logger = logging.getLogger(__name__)

class CacheService:
    """Service for caching RAG responses"""
    
    def __init__(self):
        self.redis_client = None
        self.enabled = False
    
    def initialize(self, host: str = "localhost", port: int = 6379, db: int = 0):
        """Initialize Redis connection"""
        try:
            import redis
            self.redis_client = redis.Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=True,
                socket_connect_timeout=2
            )
            # Test connection
            self.redis_client.ping()
            self.enabled = True
            logger.info(f"Redis cache initialized: {host}:{port}")
        except ImportError:
            logger.warning("Redis not installed. Caching disabled. Install: pip install redis")
            self.enabled = False
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Caching disabled.")
            self.enabled = False
    
    def _generate_key(self, query: str, lang: str = "en", filters: dict = None) -> str:
        """Generate cache key from query parameters"""
        cache_data = {
            "query": query.lower().strip(),
            "lang": lang,
            "filters": filters or {}
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return f"rag:{hashlib.md5(cache_str.encode()).hexdigest()}"
    
    def get_cached_response(self, query: str, lang: str = "en", filters: dict = None) -> Optional[dict]:
        """Get cached RAG response"""
        if not self.enabled:
            return None
        
        try:
            key = self._generate_key(query, lang, filters)
            cached = self.redis_client.get(key)
            
            if cached:
                logger.info(f"Cache HIT: {query[:50]}...")
                return json.loads(cached)
            
            logger.debug(f"Cache MISS: {query[:50]}...")
            return None
        
        except Exception as e:
            logger.error(f"Cache retrieval error: {e}")
            return None
    
    def cache_response(self, query: str, response: dict, lang: str = "en", 
                      filters: dict = None, ttl: int = 3600):
        """Cache RAG response (default 1 hour TTL)"""
        if not self.enabled:
            return
        
        try:
            key = self._generate_key(query, lang, filters)
            self.redis_client.setex(
                key,
                ttl,
                json.dumps(response)
            )
            logger.debug(f"Cached response: {query[:50]}... (TTL: {ttl}s)")
        
        except Exception as e:
            logger.error(f"Cache storage error: {e}")
    
    def invalidate_cache(self, pattern: str = "rag:*"):
        """Invalidate cache by pattern"""
        if not self.enabled:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                deleted = self.redis_client.delete(*keys)
                logger.info(f"Invalidated {deleted} cache entries")
                return deleted
            return 0
        
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
            return 0
    
    def get_cache_stats(self) -> dict:
        """Get cache statistics"""
        if not self.enabled:
            return {"enabled": False}
        
        try:
            info = self.redis_client.info()
            keys_count = len(self.redis_client.keys("rag:*"))
            
            return {
                "enabled": True,
                "keys_count": keys_count,
                "memory_used": info.get("used_memory_human", "N/A"),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "hit_rate": round(
                    info.get("keyspace_hits", 0) / 
                    max(info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1) * 100, 
                    2
                )
            }
        
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {"enabled": True, "error": str(e)}

# Global cache service instance
cache_service = CacheService()
