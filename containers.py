from dependency_injector import containers, providers
from src.core.config import Config
import aioredis
import logging
from typing import Optional
import asyncio


class Container(containers.DeclarativeContainer):
    """Dependency Injection Container"""

    # Configuration provider
    config = providers.Singleton(Config)

    # Redis connection pool provider
    redis_pool: Optional[aioredis.Redis] = None

    async def initialize(self):
        """Initialize container resources"""
        logging.info("Initializing container resources...")

        # Initialize Redis connection pool if configured
        redis_config = self.config().redis
        if redis_config:
            self.redis_pool = await aioredis.from_url(
                f"redis://{redis_config.host}:{redis_config.port}",
                password=redis_config.password or None,
                encoding="utf-8",
                decode_responses=True,
            )
            logging.info("Redis connection pool initialized")

    async def shutdown_resources(self):
        """Cleanup container resources"""
        logging.info("Shutting down container resources...")

        # Close Redis connection pool if it exists
        if self.redis_pool:
            await self.redis_pool.close()
            await self.redis_pool.wait_closed()
            logging.info("Redis connection pool closed")
