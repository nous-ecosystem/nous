from .connection import engine, Base
import asyncio


async def init_models():
    """
    Create database tables for all defined models
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def initialize_database():
    """
    Synchronous wrapper to initialize database
    """
    asyncio.run(init_models())
