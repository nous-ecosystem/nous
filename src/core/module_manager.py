from pathlib import Path
import importlib
import sys

from discord.ext import commands
from dependency_injector.wiring import inject, Provide
from dependency_injector.providers import Factory

from src.core.bot import DiscordBot


class ModuleManager:
    """
    Manages dynamic loading of Discord bot modules (cogs) with dependency injection support.
    """

    @inject
    def __init__(
        self,
        bot: commands.Bot = Provide["Container.discord_bot"],
        logger=Provide["Container.logger"],
    ):
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

        Args:
            base_path: Base directory to search for modules
        """
        base_dir = Path(base_path)

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

            # Convert path to a module import path
            relative_path = module_path.relative_to(Path.cwd())
            module_name = str(relative_path).replace("/", ".").replace("\\", ".")[:-3]

            try:
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


def add_module_manager_to_container(container):
    """
    Add ModuleManager as a provider to the dependency injection container.

    Args:
        container: Dependency injection container
    """
    container.module_manager = Factory(
        ModuleManager, bot=container.discord_bot, logger=container.logger
    )


def configure_container(container):
    """
    Configure the dependency injection container.
    """
    container.wire(
        modules=[
            "src.core.bot",
            "src.core.module_manager",
            "src.injection",
        ]
    )

    # Add module manager to container
    add_module_manager_to_container(container)


# Update initialize_bot to use string-based providers
@inject
def initialize_bot(
    bot: DiscordBot = Provide["Container.discord_bot"],
    module_manager_provider: Factory = Provide["Container.module_manager"],
) -> DiscordBot:
    """
    Initialize the bot and load modules.
    """
    # Create a concrete module_manager instance
    module_manager = module_manager_provider()

    # Load modules
    module_manager.load_modules()

    return bot
