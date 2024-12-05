import os
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from src.utils.logger import logger
from typing import List, Optional
from alembic.runtime.environment import EnvironmentContext
import asyncio
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import text


class MigrationManager:
    def __init__(self, engine: AsyncEngine):
        if not engine:
            raise ValueError("Engine must be provided to MigrationManager")
        self.alembic_cfg = Config("alembic.ini")
        self.engine = engine

    async def get_current_revision(self) -> Optional[str]:
        """Get the current database revision"""
        try:

            def get_revision():
                with self.alembic_cfg.attributes.engine.connect() as conn:
                    context = EnvironmentContext(
                        self.alembic_cfg,
                        self.alembic_cfg.attributes.get("environment_script"),
                    )
                    return context.get_current_revision(conn)

            return await asyncio.to_thread(get_revision)
        except Exception as e:
            logger.error(f"Failed to get current revision: {e}")
            return None

    async def get_pending_migrations(self) -> List[str]:
        """Get a list of pending migrations"""
        try:

            def get_pending():
                script = ScriptDirectory.from_config(self.alembic_cfg)
                with self.alembic_cfg.attributes.engine.connect() as conn:
                    context = EnvironmentContext(
                        self.alembic_cfg,
                        self.alembic_cfg.attributes.get("environment_script"),
                    )
                    current = context.get_current_revision(conn)
                    pending = []
                    for rev in script.iterate_revisions(current, "head"):
                        if rev.revision != current:
                            pending.append(rev.revision)
                    return pending

            return await asyncio.to_thread(get_pending)
        except Exception as e:
            logger.error(f"Failed to get pending migrations: {e}")
            return []

    async def create_migration(self, message: str, autogenerate: bool = True) -> None:
        """Create a new migration"""
        logger.info(f"Starting migration creation: {message}")
        try:
            await asyncio.to_thread(
                command.revision,
                self.alembic_cfg,
                message=message,
                autogenerate=autogenerate,
            )
            logger.info(f"Migration created successfully: {message}")
        except Exception as e:
            logger.error(f"Failed to create migration: {e}")
            raise

    async def upgrade(self, revision: str = "head") -> None:
        """Upgrade database to a later version"""
        logger.info(f"Starting upgrade to revision: {revision}")
        try:
            await asyncio.to_thread(command.upgrade, self.alembic_cfg, revision)
            logger.info(f"Upgrade completed successfully to: {revision}")
        except Exception as e:
            logger.error(f"Failed to upgrade: {e}")
            raise

    async def downgrade(self, revision: str) -> None:
        """Downgrade database to a previous version"""
        logger.info(f"Starting downgrade to revision: {revision}")
        try:
            await asyncio.to_thread(command.downgrade, self.alembic_cfg, revision)
            logger.info(f"Downgrade completed successfully to: {revision}")
        except Exception as e:
            logger.error(f"Failed to downgrade: {e}")
            raise

    async def stamp(self, revision: str) -> None:
        """Stamp the database with a specific revision without running migrations"""
        logger.info(f"Starting stamp to revision: {revision}")
        await asyncio.to_thread(command.stamp, self.alembic_cfg, revision)
        logger.info(f"Stamped database revision to: {revision}")
