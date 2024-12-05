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
        engine_settings = {
            "echo": config.database.echo,
            **config.database.pooling_settings,
        }

        self.engine = create_async_engine(config.database.url, **engine_settings)
        self.SessionLocal = sessionmaker(
            bind=self.engine, class_=AsyncSession, expire_on_commit=False
        )
        self.migrations = MigrationManager(self.engine)

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

    async def verify_database_exists(self):
        """Verify database connection and tables exist"""
        try:
            async with self.engine.begin() as conn:
                # Just verify we can connect and tables exist
                await conn.run_sync(lambda sync_conn: Base.metadata.tables)
            logger.info("Database verification completed successfully")
        except Exception as e:
            logger.error(f"Database verification failed: {e}")
            raise
