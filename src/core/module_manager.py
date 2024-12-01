from pathlib import Path
import importlib
import sys

from discord.ext import commands
from dependency_injector.wiring import inject, Provide

from src.core.bot import DiscordBot


class ModuleManager:
    """
    Manages dynamic loading of Discord bot modules (cogs) with dependency injection support.
    """

    def __init__(self, bot: commands.Bot, logger):
        """
        Initialize ModuleManager with bot and logger dependencies.

        Args:
            bot: Discord bot instance
            logger: Logging instance
        """
        self.bot = bot
        self.logger = logger
        self.loaded_modules = []

    def load_modules(self, base_path: str = "src"):
        """
        Dynamically load modules (cogs) from the specified base path.
        """
        base_dir = Path(base_path).resolve()  # Get absolute path

        # Ensure the base directory is in Python path
        if str(base_dir) not in sys.path:
            sys.path.insert(0, str(base_dir))

        # Recursively find all Python files
        for module_path in base_dir.rglob("*.py"):
            # Skip __init__.py, module_manager.py, and any files in test or utils directories
            if module_path.stem in ["__init__", "module_manager"] or any(
                x in module_path.parts for x in ["test", "utils", "core"]
            ):
                continue

            # Convert path to module import path
            try:
                module_path = module_path.resolve()  # Get absolute path
                relative_path = module_path.relative_to(Path.cwd().resolve())
                module_name = (
                    str(relative_path).replace("/", ".").replace("\\", ".")[:-3]
                )

                # Import the module
                module = importlib.import_module(module_name)

                # Check for a Cog class or setup function
                cog_class = getattr(module, "Cog", None)
                setup_func = getattr(module, "setup", None)

                if cog_class and issubclass(cog_class, commands.Cog):
                    # Instantiate and add the cog
                    cog_instance = cog_class(self.bot)
                    self.bot.add_cog(cog_instance)
                    self.loaded_modules.append(module_name)
                    self.logger.info(f"Loaded cog from {module_name}")

                elif setup_func:
                    # Call setup function if it exists
                    setup_func(self.bot)
                    self.loaded_modules.append(module_name)
                    self.logger.info(f"Loaded module {module_name} via setup function")

            except Exception as e:
                self.logger.error(f"Failed to load module {module_name}: {e}")

        self.logger.info(f"Total modules loaded: {len(self.loaded_modules)}")

    def get_loaded_modules(self):
        """
        Retrieve the list of successfully loaded modules.

        Returns:
            List of loaded module names
        """
        return self.loaded_modules
