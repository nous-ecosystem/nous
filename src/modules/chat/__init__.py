# chat/__init__.py

from .chat import ChatCog
from .events import setup_events


def setup(bot):
    cog = ChatCog(bot)
    bot.add_cog(cog)
    setup_events(bot, cog)
