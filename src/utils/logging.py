import logging
import sys
from typing import Optional
from pathlib import Path
from dependency_injector import containers, providers
from src.core.config import LogConfig
from logging.handlers import RotatingFileHandler


class BotLogger:
    """
    A logger class for the Discord bot that provides centralized logging functionality.
    Compatible with dependency_injector for dependency injection.
    Maintains only the last 2 log files with tracebacks.
    """

    def __init__(self, log_config: LogConfig) -> None:
        """
        Initialize the logger with configuration from dependency injection.

        Args:
            log_config: Logging configuration provided via dependency injection
        """
        self.logger = logging.getLogger("DiscordBot")
        self.logger.setLevel(getattr(logging, log_config.level.upper()))

        # Create logs directory if it doesn't exist
        log_dir = Path(log_config.directory)
        log_dir.mkdir(exist_ok=True)

        # File handler with rotation
        file_handler = RotatingFileHandler(
            filename=log_dir / "discord_bot.log",
            encoding="utf-8",
            mode="a",
            maxBytes=5 * 1024 * 1024,  # 5MB per file
            backupCount=1,  # Keep 1 backup file (2 files total)
        )
        file_handler.setFormatter(self._get_formatter())

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self._get_formatter())

        # Add handlers if they don't exist
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    @staticmethod
    def _get_formatter() -> logging.Formatter:
        """Return a custom formatter for the logger."""
        return logging.Formatter(
            "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def info(self, message: str) -> None:
        """Log an info level message."""
        self.logger.info(message)

    def warning(self, message: str) -> None:
        """Log a warning level message."""
        self.logger.warning(message)

    def error(self, message: str) -> None:
        """Log an error level message."""
        self.logger.error(message)

    def debug(self, message: str) -> None:
        """Log a debug level message."""
        self.logger.debug(message)

    def critical(self, message: str) -> None:
        """Log a critical level message."""
        self.logger.critical(message)


class LoggerContainer(containers.DeclarativeContainer):
    """Dependency Injection container for logging."""

    # Get config from the config container
    config = providers.Dependency()

    # Create logger with injected config
    logger = providers.Singleton(BotLogger, log_config=providers.Dependency())
