# chat/__init__.py

from .chat import ChatCog
from .events import setup_events
from dependency_injector.wiring import inject, Provide
from src.containers import Container


@inject
def setup(
    bot,
    llm_manager=Provide[Container.llm.llm_manager],
    db_manager=Provide[Container.database.db_manager],
    config=Provide[Container.config.config],
):
    """Initialize the chat module with dependencies."""
    cog = ChatCog(bot, llm_manager, db_manager, config)
    bot.add_cog(cog)
    setup_events(bot, cog)
