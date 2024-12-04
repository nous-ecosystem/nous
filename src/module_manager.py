import os
import importlib
import inspect
from typing import List
import discord
from discord.ext import commands
from src.utils.logger import logger


class ModuleManager:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cogs_path = os.path.join(os.path.dirname(__file__), "cogs")

    async def load_all_modules(self) -> List[str]:
        """
        Automatically loads all cog modules from the cogs directory

        Returns:
            List[str]: List of loaded module names
        """
        loaded_modules = []

        # Ensure the cogs directory exists
        if not os.path.exists(self.cogs_path):
            logger.warning(f"Cogs directory not found at {self.cogs_path}")
            return loaded_modules

        # Iterate through all files in the cogs directory
        for filename in os.listdir(self.cogs_path):
            if filename.endswith(".py") and not filename.startswith("_"):
                try:
                    # Convert filename to module path
                    module_name = f"src.cogs.{filename[:-3]}"

                    # Import the module
                    module = importlib.import_module(module_name)

                    # Find all cog classes in the module
                    for name, obj in inspect.getmembers(module):
                        if (
                            inspect.isclass(obj)
                            and issubclass(obj, commands.Cog)
                            and obj != commands.Cog
                        ):
                            await self.bot.add_cog(obj(self.bot))
                            loaded_modules.append(module_name)
                            logger.info(f"Loaded cog: {name} from {module_name}")

                except Exception as e:
                    logger.error(f"Failed to load module {filename}: {str(e)}")

        return loaded_modules

    async def reload_module(self, module_name: str) -> bool:
        """
        Reloads a specific module

        Args:
            module_name (str): Name of the module to reload

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            await self.bot.reload_extension(f"src.cogs.{module_name}")
            logger.info(f"Reloaded module: {module_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to reload module {module_name}: {str(e)}")
            return False
