import json
import redis.asyncio as redis
from typing import Optional, Any
from app.core.config import settings

# Redis connection pool
redis_pool = redis.ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=1,  # Use different DB for cache
    decode_responses=True
)
redis_client = redis.Redis(connection_pool=redis_pool)


class CacheService:
    def __init__(self):
        self.redis = redis_client
        self.default_ttl = 300  # 5 minutes default TTL

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = await self.redis.get(key)
            if value is not None:
                return json.loads(value)
            return None
        except Exception:
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        try:
            if ttl is None:
                ttl = self.default_ttl
            await self.redis.set(
                key, 
                json.dumps(value, default=str), 
                ex=ttl
            )
            return True
        except Exception:
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            await self.redis.delete(key)
            return True
        except Exception:
            return False

    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                return await self.redis.delete(*keys)
            return 0
        except Exception:
            return 0

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            return await self.redis.exists(key)
        except Exception:
            return False


# Create singleton instance
cache_service = CacheService()