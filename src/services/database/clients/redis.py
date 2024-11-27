from typing import Any, Dict, List, Optional, Union
import json
import redis.asyncio as redis

from ..client import CacheableDatabase


class RedisClient(CacheableDatabase):
    """Redis client implementation for caching."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        **kwargs,
    ):
        """Initialize Redis client.

        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            password: Redis password
            **kwargs: Additional connection parameters
        """
        self._connection_params = {
            "host": host,
            "port": port,
            "db": db,
            "password": password,
            **kwargs,
        }
        self._client: Optional[redis.Redis] = None

    async def connect(self) -> None:
        """Establish connection to Redis."""
        self._client = redis.Redis(**self._connection_params)
        # Test connection
        await self._client.ping()

    async def disconnect(self) -> None:
        """Close the Redis connection."""
        if self._client:
            await self._client.close()
            self._client = None

    async def get_session(self) -> redis.Redis:
        """Get Redis client instance."""
        if not self._client:
            raise RuntimeError("Redis not connected")
        return self._client

    async def create(self, model: Any, data: Dict[str, Any]) -> Any:
        """Create a new record in Redis."""
        if not hasattr(model, "__name__"):
            raise ValueError("Model must have a __name__ attribute")

        key = f"{model.__name__}:{data.get('id', '')}"
        client = await self.get_session()
        await client.set(key, json.dumps(data))
        return data

    async def read(self, model: Any, id: Union[str, int]) -> Optional[Any]:
        """Read a record from Redis."""
        if not hasattr(model, "__name__"):
            raise ValueError("Model must have a __name__ attribute")

        key = f"{model.__name__}:{id}"
        client = await self.get_session()
        data = await client.get(key)
        return json.loads(data) if data else None

    async def update(
        self, model: Any, id: Union[str, int], data: Dict[str, Any]
    ) -> Any:
        """Update a record in Redis."""
        if not hasattr(model, "__name__"):
            raise ValueError("Model must have a __name__ attribute")

        key = f"{model.__name__}:{id}"
        client = await self.get_session()

        # Get existing data
        existing = await client.get(key)
        if not existing:
            return None

        # Update data
        updated = {**json.loads(existing), **data}
        await client.set(key, json.dumps(updated))
        return updated

    async def delete(self, model: Any, id: Union[str, int]) -> bool:
        """Delete a record from Redis."""
        if not hasattr(model, "__name__"):
            raise ValueError("Model must have a __name__ attribute")

        key = f"{model.__name__}:{id}"
        client = await self.get_session()
        return bool(await client.delete(key))

    async def query(self, model: Any, filters: Dict[str, Any]) -> List[Any]:
        """Query records from Redis using pattern matching."""
        if not hasattr(model, "__name__"):
            raise ValueError("Model must have a __name__ attribute")

        client = await self.get_session()
        pattern = f"{model.__name__}:*"
        keys = await client.keys(pattern)

        if not keys:
            return []

        # Get all values
        pipeline = client.pipeline()
        for key in keys:
            pipeline.get(key)

        values = await pipeline.execute()
        results = [json.loads(value) for value in values if value]

        # Apply filters
        return [
            item
            for item in results
            if all(item.get(k) == v for k, v in filters.items())
        ]

    async def execute_raw(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Execute a raw Redis command."""
        client = await self.get_session()
        command_parts = query.split()
        if params:
            command_parts.extend(str(v) for v in params.values())
        return await client.execute_command(*command_parts)

    async def cache_set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a cache value."""
        client = await self.get_session()
        serialized = (
            json.dumps(value)
            if not isinstance(value, (str, int, float, bool))
            else str(value)
        )
        if ttl:
            await client.setex(key, ttl, serialized)
        else:
            await client.set(key, serialized)

    async def cache_get(self, key: str) -> Optional[Any]:
        """Get a cached value."""
        client = await self.get_session()
        value = await client.get(key)
        if not value:
            return None

        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value.decode()

    async def cache_delete(self, key: str) -> None:
        """Delete a cached value."""
        client = await self.get_session()
        await client.delete(key)
