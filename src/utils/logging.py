import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional


class LoggerResolver:
    _instance: Optional["BotLogger"] = None

    @classmethod
    def get_logger(cls, log_level: str = "INFO", log_dir: str = "logs") -> "BotLogger":
        if cls._instance is None:
            cls._instance = BotLogger(log_level, log_dir)
        return cls._instance


class BotLogger:
    """Singleton logger class for the Discord bot"""

    def __init__(self, log_level: str = "INFO", log_dir: str = "logs"):
        # Prevent multiple logger instances
        if hasattr(logging.getLogger("DiscordBot"), "handlers"):
            self.logger = logging.getLogger("DiscordBot")
            return

        self.logger = logging.getLogger("DiscordBot")
        self.logger.setLevel(getattr(logging, log_level.upper()))

        # Create logs directory if it doesn't exist
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self._get_formatter())
        self.logger.addHandler(console_handler)

        # File handler with rotation
        file_handler = RotatingFileHandler(
            log_path / "discord_bot.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(self._get_formatter())
        self.logger.addHandler(file_handler)

    def _get_formatter(self) -> logging.Formatter:
        return logging.Formatter(
            "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"
        )

    def debug(self, message: str):
        self.logger.debug(message)

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)

    def critical(self, message: str):
        self.logger.critical(message)

    def cleanup(self):
        """Cleanup logging handlers"""
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)
        self.logger.info("Logger shutdown complete")
