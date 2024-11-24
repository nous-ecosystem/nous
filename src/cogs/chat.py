from discord.ext import commands
from dependency_injector.wiring import inject, Provide
from containers import Container
from services.llm.manager import LLMManager


class ChatCog(commands.Cog):
    @inject
    def __init__(self, bot, llm: LLMManager = Provide[Container.main_llm]):
        self.bot = bot
        self.llm = llm

    @commands.command()
    async def chat(self, ctx, *, message: str):
        provider = self.llm.get_provider("openai")
        response = await provider.chat(messages=[{"role": "user", "content": message}])
        await ctx.send(response)


async def setup(bot):
    await bot.add_cog(ChatCog(bot))
