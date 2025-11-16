from redis.asyncio import from_url, Redis
from backend.api.core.config import settings

_redis: Redis | None = None

async def get_redis() -> Redis:
    """Global Redis connection (async)."""
    global _redis
    if _redis is None:
        _redis = from_url(
            settings.REDIS_URL,
            decode_responses=True,        # strings in/out
            health_check_interval=30,
        )
    return _redis

async def close_redis():
    global _redis
    if _redis is not None:
        await _redis.aclose()
        _redis = None
