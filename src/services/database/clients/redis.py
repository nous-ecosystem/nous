from typing import Any, Dict, List, Optional
import json
import redis.asyncio as redis
from redis.asyncio.client import Redis
from redis.exceptions import ResponseError

from ..client import RedisInterface


class RedisClient(RedisInterface):
    """Redis client implementation with RedisJSON support using Redis Stack."""

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
        self._client: Optional[Redis] = None

    async def connect(self) -> None:
        """Establish connection to Redis."""
        self._client = redis.Redis(
            **self._connection_params,
            decode_responses=True,
            # Enable Redis Stack features
            protocol=3,
        )
        # Test connection
        await self._client.ping()

    async def disconnect(self) -> None:
        """Close the Redis connection."""
        if self._client:
            await self._client.close()
            self._client = None

    def _get_client(self) -> Redis:
        """Get Redis client instance."""
        if not self._client:
            raise RuntimeError("Redis not connected")
        return self._client

    async def json_set(self, key: str, value: Any) -> bool:
        """Set a JSON value using RedisJSON."""
        client = self._get_client()
        try:
            # Use native JSON interface
            result = client.json().set(key, "$", value)
            return result is True
        except ResponseError:
            return False

    async def json_get(self, key: str) -> Optional[Any]:
        """Get a JSON value using RedisJSON."""
        client = self._get_client()
        try:
            # Use native JSON interface
            return client.json().get(key)
        except ResponseError:
            return None

    async def json_delete(self, key: str) -> bool:
        """Delete a JSON value using RedisJSON."""
        client = self._get_client()
        try:
            # Use native JSON interface
            result = client.json().delete(key)
            return bool(result)
        except ResponseError:
            return False

    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """Set a string value."""
        client = self._get_client()
        return await client.set(key, value, ex=ttl) is True

    async def get(self, key: str) -> Optional[str]:
        """Get a string value."""
        client = self._get_client()
        value = await client.get(key)
        return value if value is not None else None

    async def delete(self, key: str) -> bool:
        """Delete a value."""
        client = self._get_client()
        return bool(await client.delete(key))
