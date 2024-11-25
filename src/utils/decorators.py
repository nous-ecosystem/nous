from functools import wraps
from typing import Type, TypeVar, Callable
from .logging import LoggerResolver

T = TypeVar("T")


def with_logger(cls: Type[T]) -> Type[T]:
    """Class decorator to automatically inject logger"""
    original_init = cls.__init__

    @wraps(cls.__init__)
    def new_init(self, *args, **kwargs):
        self.logger = LoggerResolver.get_logger()
        original_init(self, *args, **kwargs)

    cls.__init__ = new_init
    return cls
