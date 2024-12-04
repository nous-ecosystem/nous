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
        self.loaded_modules = []

    async def load_all_modules(self) -> List[str]:
        """
        Automatically loads all cog modules from the cogs directory

        Returns:
            List[str]: List of loaded module names
        """
        # Ensure the cogs directory exists
        if not os.path.exists(self.cogs_path):
            logger.warning(f"Cogs directory not found at {self.cogs_path}")
            return self.loaded_modules

        # Walk through all subdirectories in the cogs path
        for root, dirs, files in os.walk(self.cogs_path):
            for filename in files:
                if filename.endswith(".py") and not filename.startswith("_"):
                    try:
                        # Get the relative path from cogs directory
                        rel_path = os.path.relpath(root, self.cogs_path)
                        # Convert path to module notation
                        if rel_path == ".":
                            module_path = f"src.cogs.{filename[:-3]}"
                        else:
                            module_path = f"src.cogs.{rel_path.replace(os.sep, '.')}.{filename[:-3]}"

                        # Import the module
                        module = importlib.import_module(module_path)

                        # Find all cog classes in the module
                        for name, obj in inspect.getmembers(module):
                            if (
                                inspect.isclass(obj)
                                and issubclass(obj, commands.Cog)
                                and obj != commands.Cog
                            ):
                                if hasattr(obj, "setup"):
                                    await obj.setup(self.bot)
                                else:
                                    await self.bot.add_cog(obj(self.bot))
                                self.loaded_modules.append(module_path)
                                logger.info(f"Loaded cog: {name} from {module_path}")

                    except Exception as e:
                        logger.error(f"Failed to load module {filename}: {str(e)}")

        return self.loaded_modules

    async def reload_module(self, module_name: str) -> bool:
        """
        Reloads a specific module

        Args:
            module_name (str): Name of the module to reload

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Remove the cog first
            await self.bot.reload_extension(f"src.cogs.{module_name}")
            logger.info(f"Reloaded module: {module_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to reload module {module_name}: {str(e)}")
            return False

    async def unload_all_modules(self):
        """Unload all currently loaded modules"""
        for module in self.loaded_modules:
            try:
                await self.bot.unload_extension(module)
                logger.info(f"Unloaded module: {module}")
            except Exception as e:
                logger.error(f"Failed to unload module {module}: {str(e)}")
