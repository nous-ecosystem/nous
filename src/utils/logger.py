import logging
import functools
import threading


class ColorFormatter:
    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[94m",  # Blue
        "INFO": "\033[92m",  # Green
        "WARNING": "\033[93m",  # Yellow
        "ERROR": "\033[91m",  # Red
        "CRITICAL": "\033[95m",  # Magenta
    }
    RESET = "\033[0m"

    @classmethod
    def colorize(cls, level, message):
        color = cls.COLORS.get(level.upper(), "")
        return f"{color}{message}{cls.RESET}"


class Logger:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self._logger = logging.getLogger("DiscordAIBot")
        self._logger.setLevel(logging.INFO)

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Custom log formatting with color
        class ColoredFormatter(logging.Formatter):
            def format(self, record):
                original_format = "%(asctime)s - %(levelname)s - %(message)s"
                formatter = logging.Formatter(
                    original_format, datefmt="%Y-%m-%d %H:%M:%S"
                )
                formatted_message = formatter.format(record)
                return ColorFormatter.colorize(record.levelname, formatted_message)

        console_handler.setFormatter(ColoredFormatter())
        self._logger.addHandler(console_handler)

    @classmethod
    def get_instance(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    @functools.lru_cache(maxsize=128)
    def info(self, message):
        self._logger.info(message)

    @functools.lru_cache(maxsize=128)
    def error(self, message):
        self._logger.error(message)

    @functools.lru_cache(maxsize=128)
    def warning(self, message):
        self._logger.warning(message)

    @functools.lru_cache(maxsize=128)
    def debug(self, message):
        self._logger.debug(message)


# Create a singleton instance
logger = Logger.get_instance()
