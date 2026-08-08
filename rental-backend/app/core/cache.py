# app/core/cache.py
import json
import hashlib
from typing import Any, Optional, Callable
from functools import wraps
import redis.asyncio as aioredis
from app.config import settings


class CacheManager:
    """Redis cache manager with pattern-based invalidation."""

    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None

    async def connect(self):
        self.redis = aioredis.from_url(
            settings.REDIS_URL, decode_responses=True
        )

    async def disconnect(self):
        if self.redis:
            await self.redis.close()

    def _make_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from function arguments."""
        key_data = json.dumps(
            {"args": str(args), "kwargs": str(kwargs)}, sort_keys=True
        )
        key_hash = hashlib.md5(key_data.encode()).hexdigest()[:12]
        return f"{prefix}:{key_hash}"

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        data = await self.redis.get(key)
        if data:
            return json.loads(data)
        return None

    async def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache with TTL."""
        await self.redis.set(key, json.dumps(value, default=str), ex=ttl)

    async def delete(self, key: str):
        """Delete value from cache."""
        await self.redis.delete(key)

    async def invalidate_pattern(self, pattern: str):
        """Delete all keys matching pattern."""
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)

    async def get_or_set(
        self,
        key: str,
        factory: Callable,
        ttl: int = 3600,
    ) -> Any:
        """Get from cache or compute and cache."""
        cached = await self.get(key)
        if cached is not None:
            return cached

        value = await factory()
        await self.set(key, value, ttl)
        return value


cache = CacheManager()


def cached(prefix: str, ttl: int = 3600):
    """Decorator for caching function results."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = cache._make_key(prefix, *args, **kwargs)
            return await cache.get_or_set(
                key, lambda: func(*args, **kwargs), ttl
            )
        return wrapper

    return decorator
