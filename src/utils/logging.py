import logging
from dependency_injector import containers, providers
from rich.logging import RichHandler


class SingletonLogger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SingletonLogger, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.logger = logging.getLogger("discord_bot")
        self.logger.setLevel(logging.DEBUG)
        handler = RichHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def get_logger(self):
        return self.logger


class LoggerContainer(containers.DeclarativeContainer):
    logger = providers.Singleton(SingletonLogger)


# Usage example:
# from src.logging import LoggerContainer
# logger = LoggerContainer.logger().get_logger()
# logger.info("This is an info message")
