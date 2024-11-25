from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .models.base import Base


async def init_database(db_url: str):
    """Initialize database connection and create tables"""
    engine = create_async_engine(
        db_url,
        echo=False,
        pool_size=20,
        max_overflow=30,
        pool_timeout=30,
        pool_pre_ping=True,
        pool_recycle=3600,
    )

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    return engine, async_session
