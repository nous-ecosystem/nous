from redis import asyncio as aioredis
from typing import Optional, Any
import json


class RedisManager:
    def __init__(self, redis_url: str = "redis://localhost"):
        self.redis_url = redis_url
        self.redis: Optional[aioredis.Redis] = None

    async def init_redis(self):
        if not self.redis:
            self.redis = await aioredis.from_url(self.redis_url)

    async def close(self):
        if self.redis:
            await self.redis.close()

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        await self.init_redis()
        value = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
        return await self.redis.set(key, value, ex=ttl)

    async def get(self, key: str, default: Any = None) -> Any:
        await self.init_redis()
        value = await self.redis.get(key)
        if value is None:
            return default
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value.decode()

    async def delete(self, key: str) -> bool:
        await self.init_redis()
        return await self.redis.delete(key) > 0
