from enum import Enum
from typing import Dict, Optional, cast
import logging
from .client import RedisInterface, VectorInterface
from .clients.redis import RedisClient
from .clients.lancedb import LanceDBClient


class DatabaseType(Enum):
    """Supported database types."""

    REDIS = "redis"
    LANCEDB = "lancedb"


class DatabaseManager:
    """Manages database connections for Redis and LanceDB."""

    def __init__(self):
        self._redis: Optional[RedisInterface] = None
        self._vector_db: Optional[VectorInterface] = None
        self._config: Dict[str, Dict] = {}
        self.logger = logging.getLogger("database_manager")

    async def setup(self) -> None:
        """Initialize database connections."""
        # Get configuration from container
        from src.containers import config

        # Configure database connections
        self.configure(
            redis_config={
                "host": config.redis.host,
                "port": config.redis.port,
                "password": config.redis.password,
            },
            vector_config={"uri": "data/vectors"},
        )

        try:
            # Initialize Redis if configured
            if "redis" in self._config:
                self._redis = RedisClient(**self._config["redis"])
                await self._redis.connect()

            # Initialize vector database if configured
            if "vector" in self._config:
                self._vector_db = LanceDBClient(**self._config["vector"])
                await self._vector_db.connect()

                # Create default collections after successful connection
                try:
                    await self._vector_db.create_collection(
                        "message_embeddings", dimension=1536
                    )
                except Exception as e:
                    self.logger.warning(
                        f"Failed to create default collection: {str(e)}"
                    )

        except Exception as e:
            await self.close_all()  # Clean up on error
            raise RuntimeError(f"Failed to initialize database connections: {str(e)}")

    def configure(
        self, redis_config: Optional[Dict] = None, vector_config: Optional[Dict] = None
    ) -> None:
        """Configure database connections.

        Args:
            redis_config: Redis configuration parameters
            vector_config: Vector database configuration parameters
        """
        if redis_config:
            self._config["redis"] = redis_config
        if vector_config:
            self._config["vector"] = vector_config

    async def get_redis(self) -> RedisInterface:
        """Get Redis client instance."""
        if not self._redis:
            if "redis" not in self._config:
                raise ValueError("Redis not configured")

            self._redis = RedisClient(**self._config["redis"])
            await self._redis.connect()

        return self._redis

    async def get_vector_db(self) -> VectorInterface:
        """Get vector database client instance."""
        if not self._vector_db:
            if "vector" not in self._config:
                raise ValueError("Vector database not configured")

            self._vector_db = LanceDBClient(**self._config["vector"])
            await self._vector_db.connect()

        return self._vector_db

    async def close_all(self) -> None:
        """Close all database connections."""
        if self._redis:
            await self._redis.disconnect()
            self._redis = None

        if self._vector_db:
            await self._vector_db.disconnect()
            self._vector_db = None


# Global database manager instance
db_manager = DatabaseManager()
