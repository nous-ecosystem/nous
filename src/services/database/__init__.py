from typing import Optional, Dict, Any
from .manager import DatabaseManager, DatabaseType, db_manager
from .client import RedisInterface, VectorInterface

__all__ = [
    "DatabaseManager",
    "DatabaseType",
    "RedisInterface",
    "VectorInterface",
    "setup_databases",
]


async def setup_databases(
    redis_config: Optional[Dict[str, Any]] = None,
    vector_config: Optional[Dict[str, Any]] = None,
) -> None:
    """Initialize database connections.

    Example usage:
        await setup_databases(
            redis_config={
                "host": "localhost",
                "port": 6379,
                "password": "secret"
            },
            vector_config={
                "uri": "data/vectors"
            }
        )

        # Get Redis client
        redis = await db_manager.get_redis()
        await redis.json_set("user:1", {"name": "John"})

        # Get vector database client
        vector_db = await db_manager.get_vector_db()
        await vector_db.create_collection("embeddings", dimension=1536)
    """
    db_manager.configure(redis_config=redis_config, vector_config=vector_config)

    # Initialize vector collection if vector database is configured
    if vector_config:
        vector_db = await db_manager.get_vector_db()
        await vector_db.create_collection("message_embeddings", dimension=1536)
