import os
from alembic import command
from alembic.config import Config
from src.utils.logger import logger


class MigrationManager:
    def __init__(self):
        self.alembic_cfg = Config("alembic.ini")

    def create_migration(self, message: str):
        """Create a new migration"""
        try:
            command.revision(self.alembic_cfg, autogenerate=True, message=message)
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
