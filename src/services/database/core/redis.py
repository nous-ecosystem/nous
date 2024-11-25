from redis import asyncio as aioredis
from typing import Optional, Any, Dict, List, Union
import json
from redisvl.index import AsyncSearchIndex
from redisvl.query import VectorQuery


class RedisManager:
    def __init__(self, redis_url: str = "redis://localhost"):
        self.redis_url = redis_url
        self.redis: Optional[aioredis.Redis] = None
        self._indices: Dict[str, AsyncSearchIndex] = {}

    async def init_redis(self):
        if not self.redis:
            self.redis = await aioredis.from_url(
                self.redis_url,
                decode_responses=True,  # Auto decode for string operations
                encoding="utf-8",
            )

    async def close(self):
        if self.redis:
            await self.redis.close()
            self.redis = None

    # String operations
    async def str_set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        await self.init_redis()
        return await self.redis.set(key, value, ex=ttl)

    async def str_get(self, key: str, default: str = None) -> Optional[str]:
        await self.init_redis()
        value = await self.redis.get(key)
        return value if value is not None else default

    # Hash operations
    async def hash_set(self, key: str, mapping: Dict[str, Any]) -> bool:
        await self.init_redis()
        return await self.redis.hset(key, mapping=mapping)

    async def hash_get(self, key: str, field: str) -> Any:
        await self.init_redis()
        return await self.redis.hget(key, field)

    async def hash_get_all(self, key: str) -> Dict[str, Any]:
        await self.init_redis()
        return await self.redis.hgetall(key)

    # JSON operations
    async def json_set(self, key: str, path: str, value: Any) -> bool:
        await self.init_redis()
        return await self.redis.json().set(key, path, value)

    async def json_get(self, key: str, path: str = ".", default: Any = None) -> Any:
        await self.init_redis()
        try:
            value = await self.redis.json().get(key, path)
            return value if value is not None else default
        except Exception:
            return default

    # Vector operations
    async def create_vector_index(
        self, schema: Dict[str, Any], overwrite: bool = False
    ) -> AsyncSearchIndex:
        """Create a vector search index from schema"""
        index = AsyncSearchIndex.from_dict(schema)
        await index.set_client(self.redis)
        await index.create(overwrite=overwrite)
        self._indices[schema["index"]["name"]] = index
        return index

    async def vector_search(
        self,
        index_name: str,
        vector: List[float],
        vector_field: str,
        return_fields: List[str] = None,
        num_results: int = 10,
    ) -> List[Dict[str, Any]]:
        """Perform vector similarity search"""
        if index_name not in self._indices:
            raise ValueError(f"Index {index_name} not found. Create it first.")

        query = VectorQuery(
            vector=vector,
            vector_field_name=vector_field,
            return_fields=return_fields,
            num_results=num_results,
        )

        results = await self._indices[index_name].query(query)
        return results.docs

    # Common operations
    async def delete(self, key: str) -> bool:
        await self.init_redis()
        return await self.redis.delete(key) > 0

    async def exists(self, key: str) -> bool:
        await self.init_redis()
        return await self.redis.exists(key) > 0

    async def expire(self, key: str, ttl: int) -> bool:
        await self.init_redis()
        return await self.redis.expire(key, ttl)
