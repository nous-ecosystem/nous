import os
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from src.utils.logger import logger
from typing import List, Optional


class MigrationManager:
    def __init__(self):
        self.alembic_cfg = Config("alembic.ini")

    def get_current_revision(self) -> Optional[str]:
        """Get the current database revision"""
        try:
            script = ScriptDirectory.from_config(self.alembic_cfg)
            with self.alembic_cfg.attributes.engine.connect() as conn:
                context = self.alembic_cfg.attributes.get("context")
                return context.get_current_revision(conn)
        except Exception as e:
            logger.error(f"Failed to get current revision: {e}")
            return None

    def get_pending_migrations(self) -> List[str]:
        """Get a list of pending migrations"""
        try:
            script = ScriptDirectory.from_config(self.alembic_cfg)
            current = self.get_current_revision()
            pending = []
            for rev in script.iterate_revisions(current, "head"):
                if rev.revision != current:
                    pending.append(rev.revision)
            return pending
        except Exception as e:
            logger.error(f"Failed to get pending migrations: {e}")
            return []

    def create_migration(self, message: str, autogenerate: bool = True):
        """Create a new migration"""
        try:
            command.revision(
                self.alembic_cfg, message=message, autogenerate=autogenerate
            )
            logger.info(f"Created new migration: {message}")
        except Exception as e:
            logger.error(f"Failed to create migration: {e}")
            raise

    def upgrade(self, revision: str = "head"):
        """Upgrade to a later version"""
        try:
            command.upgrade(self.alembic_cfg, revision)
            logger.info(f"Upgraded database to: {revision}")
        except Exception as e:
            logger.error(f"Failed to upgrade: {e}")
            raise

    def downgrade(self, revision: str):
        """Revert to a previous version"""
        try:
            command.downgrade(self.alembic_cfg, revision)
            logger.info(f"Downgraded database to: {revision}")
        except Exception as e:
            logger.error(f"Failed to downgrade: {e}")
            raise

    def stamp(self, revision: str):
        """Stamp the revision table without running migrations"""
        try:
            command.stamp(self.alembic_cfg, revision)
            logger.info(f"Stamped database revision to: {revision}")
        except Exception as e:
            logger.error(f"Failed to stamp revision: {e}")
            raise
