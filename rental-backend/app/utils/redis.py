# app/utils/redis.py
import redis.asyncio as aioredis
from app.config import settings

# Redis connection pool
redis_pool = aioredis.ConnectionPool.from_url(
    settings.REDIS_URL,
    max_connections=settings.REDIS_MAX_CONNECTIONS,
    retry_on_timeout=True,
    socket_timeout=5,
    socket_connect_timeout=5,
    decode_responses=True,
)


async def get_redis() -> aioredis.Redis:
    """Get Redis connection from pool."""
    return aioredis.Redis(connection_pool=redis_pool)


async def close_redis():
    """Close Redis connection pool."""
    await redis_pool.disconnect()
