from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

# Default to SQLite in data/sqlite directory, but allow configuration through environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///data/sqlite/bot.db")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    future=True,
)

# Create async session factory
AsyncSessionFactory = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)


async def init_db():
    """Initialize the database, creating all tables."""
    from src.database.base import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """Get a new database session."""
    async with AsyncSessionFactory() as session:
        return session
