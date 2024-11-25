from discord.ext import commands
from dependency_injector.wiring import inject, Provide
from containers import Container
from services.llm.manager import LLMManager
from utils.logging import BotLogger
from utils.decorators import with_logger


@with_logger
class ChatCog(commands.Cog):
    @inject
    def __init__(
        self,
        bot,
        llm: LLMManager = Provide[Container.main_llm],
    ):
        self.bot = bot
        self.llm = llm
        self.logger.info("ChatCog initialized")

    @commands.command()
    async def chat(self, ctx, *, message: str):
        try:
            self.logger.info(
                f"Chat command received from {ctx.author}: {message[:50]}..."
            )
            provider = self.llm.get_provider("openai")
            response = await provider.chat(
                messages=[{"role": "user", "content": message}]
            )
            await ctx.send(response)
            self.logger.info(f"Successfully processed chat command for {ctx.author}")
        except Exception as e:
            self.logger.error(f"Error processing chat command: {str(e)}")
            await ctx.send("Sorry, something went wrong processing your request.")


async def setup(bot):
    await bot.add_cog(ChatCog(bot))
