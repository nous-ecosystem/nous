from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from src.config import Config
from src.utils.logger import logger
from contextlib import asynccontextmanager
from src.database.migrations import MigrationManager
from sqlalchemy.sql import text

Base = declarative_base()


class DatabaseManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        config = Config()
        sqlite_url = "sqlite+aiosqlite:///./data/database.sqlite"
        self.engine = create_async_engine(sqlite_url, echo=False)
        self.SessionLocal = sessionmaker(
            bind=self.engine, class_=AsyncSession, expire_on_commit=False
        )
        self.migrations = MigrationManager()

    async def create_tables(self):
        """Create all tables in the database"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @asynccontextmanager
    async def get_session(self):
        """Provide a transactional scope around a series of operations"""
        session = self.SessionLocal()
        try:
            yield session
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Database error: {str(e)}")
            raise
        finally:
            await session.close()

    async def run_migrations(self):
        """Run all pending migrations"""
        self.migrations.upgrade()

    async def initialize_database(self):
        """Initialize database with tables and run pending migrations"""
        try:
            async with self.engine.begin() as conn:
                # Drop alembic_version table if it exists to start fresh
                await conn.execute(text("DROP TABLE IF EXISTS alembic_version"))

            # Create tables if they don't exist
            await self.create_tables()

            # Stamp the initial migration
            self.migrations.stamp("base")

            # Now create and run the initial migration
            self.migrations.create_migration("Initial setup", autogenerate=True)
            await self.run_migrations()

        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
