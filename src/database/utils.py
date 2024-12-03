from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from .connection import AsyncSessionLocal


@asynccontextmanager
async def get_session():
    """
    Async context manager for database sessions.
    Handles session creation, commit, and error management.
    """
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
