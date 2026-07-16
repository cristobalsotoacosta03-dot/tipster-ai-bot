"""
Cache Manager for optimizing API costs and performance.
Uses Redis (Upstash) for caching analysis results and statistics.
"""
from typing import Optional, Any, Dict
import json
import hashlib
import logging
from datetime import datetime, timedelta

from config.settings import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Redis-based cache manager for reducing API costs.
    Caches analysis results and statistics with TTL.
    """
    
    def __init__(self):
        """Initialize cache manager."""
        self.enabled = bool(settings.upstash_redis_rest_url and settings.upstash_redis_rest_token)
        self.ttl_seconds = settings.cache_ttl_seconds
        self.stats_ttl_seconds = 3600  # 1 hour for stats
        
        if self.enabled:
            try:
                from upstash_redis import Redis
                self.redis = Redis(
                    url=settings.upstash_redis_rest_url,
                    token=settings.upstash_redis_rest_token
                )
                logger.info("Cache Manager initialized with Redis (Upstash)")
            except Exception as e:
                logger.error(f"Failed to initialize Redis: {e}")
                self.enabled = False
        else:
            logger.warning("Cache Manager running in memory-only mode (Redis not configured)")
            self._memory_cache: Dict[str, tuple] = {}
    
    def _generate_key(self, prefix: str, data: Any) -> str:
        """
        Generate cache key from data.
        
        Args:
            prefix: Key prefix (e.g., 'analysis', 'stats')
            data: Data to hash
            
        Returns:
            Cache key string
        """
        data_str = json.dumps(data, sort_keys=True) if not isinstance(data, str) else data
        hash_obj = hashlib.md5(data_str.encode())
        return f"{prefix}:{hash_obj.hexdigest()}"
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        try:
            if self.enabled:
                value = self.redis.get(key)
                if value:
                    logger.debug(f"Cache HIT: {key}")
                    return json.loads(value)
            else:
                # Memory cache fallback
                if key in self._memory_cache:
                    data, expiry = self._memory_cache[key]
                    if datetime.now() < expiry:
                        logger.debug(f"Cache HIT (memory): {key}")
                        return data
                    else:
                        del self._memory_cache[key]
            
            logger.debug(f"Cache MISS: {key}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting from cache: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            ttl = ttl or self.ttl_seconds
            
            if self.enabled:
                self.redis.set(key, json.dumps(value), ex=ttl)
                logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
            else:
                # Memory cache fallback
                expiry = datetime.now() + timedelta(seconds=ttl)
                self._memory_cache[key] = (value, expiry)
                logger.debug(f"Cache SET (memory): {key}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Delete value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.enabled:
                self.redis.delete(key)
            else:
                self._memory_cache.pop(key, None)
            
            logger.debug(f"Cache DELETE: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting from cache: {e}")
            return False
    
    async def clear(self) -> bool:
        """
        Clear all cache.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.enabled:
                # Get all keys and delete them
                keys = self.redis.keys("*")
                if keys:
                    self.redis.delete(*keys)
            else:
                self._memory_cache.clear()
            
            logger.info("Cache cleared")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
    
    # ==================== SPECIALIZED CACHE METHODS ====================
    
    async def get_cached_analysis(self, match_id: str) -> Optional[Dict[str, Any]]:
        """
        Get cached analysis for a match.
        
        Args:
            match_id: Match identifier
            
        Returns:
            Cached analysis or None
        """
        key = f"analysis:{match_id}"
        return await self.get(key)
    
    async def cache_analysis(
        self,
        match_id: str,
        analysis: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """
        Cache analysis result.
        
        Args:
            match_id: Match identifier
            analysis: Analysis result to cache
            ttl: Time to live in seconds
            
        Returns:
            True if successful
        """
        key = f"analysis:{match_id}"
        ttl = ttl or self.ttl_seconds
        return await self.set(key, analysis, ttl)
    
    async def get_cached_stats(self, team_id: str) -> Optional[Dict[str, Any]]:
        """
        Get cached team statistics.
        
        Args:
            team_id: Team identifier
            
        Returns:
            Cached stats or None
        """
        key = f"stats:{team_id}"
        return await self.get(key)
    
    async def cache_stats(
        self,
        team_id: str,
        stats: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """
        Cache team statistics.
        
        Args:
            team_id: Team identifier
            stats: Statistics to cache
            ttl: Time to live in seconds
            
        Returns:
            True if successful
        """
        key = f"stats:{team_id}"
        ttl = ttl or self.stats_ttl_seconds
        return await self.set(key, stats, ttl)
    
    async def get_cached_team_info(self, team_name: str) -> Optional[Dict[str, Any]]:
        """
        Get cached team info.
        
        Args:
            team_name: Team name
            
        Returns:
            Cached team info or None
        """
        key = f"team_info:{team_name.lower()}"
        return await self.get(key)
    
    async def cache_team_info(
        self,
        team_name: str,
        team_info: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """
        Cache team information.
        
        Args:
            team_name: Team name
            team_info: Team info to cache
            ttl: Time to live in seconds
            
        Returns:
            True if successful
        """
        key = f"team_info:{team_name.lower()}"
        ttl = ttl or 86400  # 24 hours for team info
        return await self.set(key, team_info, ttl)
    
    # ==================== UTILITY METHODS ====================
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        try:
            if self.enabled:
                # upstash-redis's REST API doesn't expose INFO; dbsize is
                # the one stat it does give us for free.
                return {
                    "enabled": True,
                    "total_keys": self.redis.dbsize(),
                    "hit_rate": "N/A",  # Would need to track this
                }
            else:
                return {
                    "enabled": False,
                    "mode": "memory",
                    "cached_keys": len(self._memory_cache),
                }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"enabled": self.enabled, "error": str(e)}
    
    async def health_check(self) -> bool:
        """
        Check if cache is working.
        
        Returns:
            True if cache is working, False otherwise
        """
        try:
            test_key = "health_check_test"
            test_value = {"status": "ok", "timestamp": datetime.now().isoformat()}
            
            # Set
            await self.set(test_key, test_value, ttl=10)
            
            # Get
            retrieved = await self.get(test_key)
            
            # Delete
            await self.delete(test_key)
            
            return retrieved is not None and retrieved.get("status") == "ok"
            
        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache manager statistics.
        
        Returns:
            Dictionary with statistics
        """
        return {
            "enabled": self.enabled,
            "ttl_seconds": self.ttl_seconds,
            "stats_ttl_seconds": self.stats_ttl_seconds,
        }