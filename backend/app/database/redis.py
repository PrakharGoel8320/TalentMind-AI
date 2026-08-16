import redis.asyncio as redis
from app.core.config import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

async def get_redis() -> redis.Redis:
    yield redis_client

async def close_redis():
    await redis_client.close()
