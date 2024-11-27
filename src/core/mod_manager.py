from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import importlib.util
import types
import inspect
from discord.ext import commands
from src.utils.logging import BotLogger
from dependency_injector import containers, providers


class ModuleManager:
    """
    Manages the loading, unloading, and reloading of bot modules.
    Each module can contain events.py, commands.py, and module.py files.
    """

    def __init__(
        self, bot: commands.Bot, logger: BotLogger, modules_dir: str = "src/modules"
    ):
        """
        Initialize the module manager.

        Args:
            bot: The Discord bot instance
            logger: The bot's logger instance
            modules_dir: Directory containing module folders (default: "src/modules")
        """
        self.bot = bot
        self.logger = logger
        self.modules_dir = Path(modules_dir)
        self.loaded_modules: Dict[str, Dict[str, types.ModuleType]] = {}

    async def load_module(self, module_name: str) -> bool:
        """
        Load a module and its components (events, commands, main module).

        Args:
            module_name: Name of the module to load

        Returns:
            bool: True if module was loaded successfully, False otherwise
        """
        module_path = self.modules_dir / module_name
        if not module_path.is_dir():
            self.logger.error(f"Module directory {module_name} not found")
            return False

        module_data = {}

        # Load events.py if it exists
        events_path = module_path / "events.py"
        if events_path.exists():
            try:
                events_module = self._import_file(events_path)
                for name, obj in inspect.getmembers(events_module):
                    if inspect.iscoroutinefunction(obj) and name.startswith("on_"):
                        self.bot.event(obj)
                module_data["events"] = events_module
                self.logger.info(f"Loaded events for module {module_name}")
            except Exception as e:
                self.logger.error(f"Failed to load events for {module_name}: {str(e)}")
                return False

        # Load commands.py if it exists
        commands_path = module_path / "commands.py"
        if commands_path.exists():
            try:
                commands_module = self._import_file(commands_path)
                for name, obj in inspect.getmembers(commands_module):
                    if isinstance(obj, commands.Command):
                        self.bot.add_command(obj)
                module_data["commands"] = commands_module
                self.logger.info(f"Loaded commands for module {module_name}")
            except Exception as e:
                self.logger.error(
                    f"Failed to load commands for {module_name}: {str(e)}"
                )
                return False

        # Load module.py if it exists
        module_file_path = module_path / "module.py"
        if module_file_path.exists():
            try:
                main_module = self._import_file(module_file_path)
                module_data["main"] = main_module
                self.logger.info(f"Loaded main module file for {module_name}")
            except Exception as e:
                self.logger.error(
                    f"Failed to load main module file for {module_name}: {str(e)}"
                )
                return False

        if module_data:
            self.loaded_modules[module_name] = module_data
            self.logger.info(f"Successfully loaded module {module_name}")
            return True
        else:
            self.logger.warning(f"No loadable components found in module {module_name}")
            return False

    async def unload_module(self, module_name: str) -> bool:
        """
        Unload a module and all its components.

        Args:
            module_name: Name of the module to unload

        Returns:
            bool: True if module was unloaded successfully, False otherwise
        """
        if module_name not in self.loaded_modules:
            self.logger.warning(f"Module {module_name} is not loaded")
            return False

        module_data = self.loaded_modules[module_name]

        # Unload commands
        if "commands" in module_data:
            try:
                commands_module = module_data["commands"]
                for name, obj in inspect.getmembers(commands_module):
                    if isinstance(obj, commands.Command):
                        self.bot.remove_command(obj.name)
            except Exception as e:
                self.logger.error(
                    f"Failed to unload commands for {module_name}: {str(e)}"
                )
                return False

        # Remove event listeners
        if "events" in module_data:
            try:
                events_module = module_data["events"]
                for name, obj in inspect.getmembers(events_module):
                    if inspect.iscoroutinefunction(obj) and name.startswith("on_"):
                        self.bot.remove_listener(obj)
            except Exception as e:
                self.logger.error(
                    f"Failed to unload events for {module_name}: {str(e)}"
                )
                return False

        del self.loaded_modules[module_name]
        self.logger.info(f"Successfully unloaded module {module_name}")
        return True

    async def reload_module(self, module_name: str) -> bool:
        """
        Reload a module by unloading and loading it again.

        Args:
            module_name: Name of the module to reload

        Returns:
            bool: True if module was reloaded successfully, False otherwise
        """
        if await self.unload_module(module_name):
            return await self.load_module(module_name)
        return False

    async def load_all_modules(self) -> List[str]:
        """
        Load all modules in the modules directory.

        Returns:
            List[str]: List of successfully loaded module names
        """
        loaded_modules = []
        for module_path in self.modules_dir.iterdir():
            if module_path.is_dir() and not module_path.name.startswith("_"):
                if await self.load_module(module_path.name):
                    loaded_modules.append(module_path.name)
        return loaded_modules

    def _import_file(self, file_path: Path) -> types.ModuleType:
        """
        Import a Python file dynamically.

        Args:
            file_path: Path to the Python file to import

        Returns:
            types.ModuleType: Imported module

        Raises:
            ImportError: If the module cannot be loaded
            Exception: Any other exception that occurs during import
        """
        try:
            spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Failed to load spec for {file_path}")

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            self.logger.error(f"Failed to import {file_path}: {str(e)}")
            raise


class ModuleManagerContainer(containers.DeclarativeContainer):
    """Dependency Injection container for ModuleManager."""

    bot = providers.Dependency()
    logger = providers.Dependency()

    module_manager = providers.Singleton(ModuleManager, bot=bot, logger=logger)
