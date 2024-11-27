from enum import Enum
from typing import Dict, Optional, Type, cast
from .client import DatabaseClient, CacheableDatabase, VectorDatabase


class DatabaseType(Enum):
    """Supported database types."""

    MYSQL = "mysql"
    REDIS = "redis"
    LANCEDB = "lancedb"


class DatabaseManager:
    """Manages database connections and client instances."""

    def __init__(self):
        self._clients: Dict[str, DatabaseClient] = {}
        self._config: Dict[str, Dict] = {}

    def register_database(self, name: str, db_type: DatabaseType, config: Dict) -> None:
        """Register a database configuration."""
        self._config[name] = {"type": db_type, "config": config}

    async def get_client(self, name: str) -> Optional[DatabaseClient]:
        """Get or create a database client."""
        if name not in self._clients:
            if name not in self._config:
                raise ValueError(f"Database {name} not registered")

            await self._create_client(name)
        return self._clients[name]

    async def _create_client(self, name: str) -> None:
        """Create a new database client instance."""
        config = self._config[name]
        db_type = config["type"]

        if db_type == DatabaseType.MYSQL:
            from .clients.mysql import MySQLClient

            client = MySQLClient(**config["config"])
        elif db_type == DatabaseType.REDIS:
            from .clients.redis import RedisClient

            client = RedisClient(**config["config"])
        elif db_type == DatabaseType.LANCEDB:
            from .clients.lancedb import LanceDBClient

            client = LanceDBClient(**config["config"])
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

        await client.connect()
        # Type assertion to satisfy the type checker
        self._clients[name] = cast(DatabaseClient, client)

    async def close_all(self) -> None:
        """Close all database connections."""
        for client in self._clients.values():
            await client.disconnect()
        self._clients.clear()


# Global database manager instance
db_manager = DatabaseManager()
