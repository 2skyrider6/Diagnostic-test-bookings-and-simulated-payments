import time
from typing import Optional
import redis.asyncio as redis
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.core.config import settings

# Redis connection pool
redis_pool = redis.ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True
)
redis_client = redis.Redis(connection_pool=redis_pool)


class RateLimiter:
    def __init__(self, times: int, seconds: int):
        """
        Rate limiter.
        :param times: Maximum number of requests allowed.
        :param seconds: Time window in seconds.
        """
        self.times = times
        self.seconds = seconds
        # In-memory fallback for when Redis is unavailable
        self._fallback_cache = {}

    async def __call__(self, request: Request):
        # Use IP address as key
        ip = request.client.host if request.client else "unknown"
        # Include endpoint in key to have different limits per endpoint
        endpoint = request.url.path
        key = f"rate_limit:{ip}:{endpoint}"

        try:
            # Get current count
            current = await redis_client.get(key)
            if current is None:
                # First request, set count to 1 and expire
                await redis_client.set(key, 1, ex=self.seconds)
            else:
                current = int(current)
                if current >= self.times:
                    # Rate limit exceeded
                    raise HTTPException(
                        status_code=429,
                        detail="Too many requests",
                    )
                # Increment count
                await redis_client.incr(key)
        except Exception:
            # Fallback to in-memory rate limiting if Redis is unavailable
            current_time = time.time()
            # Clean expired entries (simple cleanup)
            self._fallback_cache = {
                k: v for k, v in self._fallback_cache.items()
                if v[1] > current_time
            }
            
            if key in self._fallback_cache:
                count, expiry_time = self._fallback_cache[key]
                if count >= self.times:
                    # Rate limit exceeded
                    raise HTTPException(
                        status_code=429,
                        detail="Too many requests",
                    )
                # Increment count
                self._fallback_cache[key] = (count + 1, expiry_time)
            else:
                # First request, set count to 1 and expire
                self._fallback_cache[key] = (1, current_time + self.seconds)

        # Return None to allow the request to proceed
        return None


# Dependency for rate limiting
def RateLimiterDep(times: int, seconds: int):
    """
    Dependency for rate limiting.
    Usage: Depends(RateLimiterDep(times=10, seconds=60))
    """
    async def rate_limiter(request: Request):
        limiter = RateLimiter(times, seconds)
        return await limiter(request)
    return rate_limiter