# src/utils/logger.py

import logging
import sys


class SingletonLogger:
    _instance = None

    class ColoredFormatter(logging.Formatter):
        COLORS = {
            "DEBUG": "\033[94m",  # Blue
            "INFO": "\033[92m",  # Green
            "WARNING": "\033[93m",  # Yellow
            "ERROR": "\033[91m",  # Red
            "CRITICAL": "\033[95m",  # Magenta
        }
        RESET = "\033[0m"

        def format(self, record):
            log_color = self.COLORS.get(record.levelname, self.RESET)
            record.msg = f"{log_color}{record.msg}{self.RESET}"
            return super().format(record)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SingletonLogger, cls).__new__(cls)
            cls._instance._initialize_logger()
        return cls._instance

    def _initialize_logger(self):
        self.logger = logging.getLogger("AIChatbotLogger")
        self.logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            self.ColoredFormatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        self.logger.addHandler(handler)

    def get_logger(self):
        return self.logger


# Usage
logger = SingletonLogger().get_logger()
logger.info("Logger initialized successfully.")
