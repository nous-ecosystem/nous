from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from src.bot.config import config
import os
import pathlib


# Resolve the absolute path for the database
def get_database_path():
    # Get the project root directory
    project_root = pathlib.Path(__file__).resolve().parents[2]

    # Create data/sqlite directory
    db_dir = project_root / "data" / "sqlite"
    db_dir.mkdir(parents=True, exist_ok=True)

    # Return full path to bot.db
    return str(db_dir / "bot.db")


# Get the correct database path
DATABASE_PATH = get_database_path()

# Create an async engine for SQLite
engine = create_async_engine(
    f"sqlite+aiosqlite:///{DATABASE_PATH}",
    echo=config.LOG_LEVEL == "DEBUG",
    future=True,
)

# Create an async session factory
AsyncSessionLocal = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

# Base class for declarative models
Base = declarative_base()
