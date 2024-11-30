import logging
from typing import Optional


class LoggerSingleton:
    _instance: Optional["LoggerSingleton"] = None
    _logger: Optional[logging.Logger] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._setup_logger()
        return cls._instance

    @classmethod
    def _setup_logger(cls):
        # Create logger
        cls._logger = logging.getLogger("discord_bot")
        cls._logger.setLevel(logging.INFO)

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)

        # Add console handler to logger
        cls._logger.addHandler(console_handler)

    @classmethod
    def get_logger(cls) -> logging.Logger:
        """
        Get the singleton logger instance.

        Returns:
            logging.Logger: Configured logger instance
        """
        if cls._logger is None:
            cls._setup_logger()
        return cls._logger

    @classmethod
    def debug(cls, msg: str):
        """Log a debug message."""
        cls.get_logger().debug(msg)

    @classmethod
    def info(cls, msg: str):
        """Log an info message."""
        cls.get_logger().info(msg)

    @classmethod
    def warning(cls, msg: str):
        """Log a warning message."""
        cls.get_logger().warning(msg)

    @classmethod
    def error(cls, msg: str):
        """Log an error message."""
        cls.get_logger().error(msg)

    @classmethod
    def critical(cls, msg: str):
        """Log a critical message."""
        cls.get_logger().critical(msg)


# Convenience function for easy importing
def get_logger():
    """
    Convenience function to get the logger instance.

    Returns:
        logging.Logger: Configured logger instance
    """
    return LoggerSingleton.get_logger()
