import importlib
import pkgutil
from typing import Dict
from discord.ext import commands
from src.utils.logger import logger
from src.config import Config


class FeatureManager:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.features: Dict[str, Dict] = {}
        self.loaded_modules: Dict[str, bool] = {}
        self.config = Config()
        logger.info("Initializing FeatureManager...")

    async def load_all_features(self):
        """Discover and load all features"""
        await self.discover_features()

        # Log discovered features once
        if self.features:
            discovered = [data["category"] for data in self.features.values()]
            logger.info(f"Discovered {len(discovered)} features...")

        return await self.load_discovered_features()

    async def discover_features(self, package_name: str = "src.cogs"):
        """Automatically discover all feature modules"""
        try:
            package = importlib.import_module(package_name)
            for _, name, is_pkg in pkgutil.iter_modules(package.__path__):
                if is_pkg:
                    await self.discover_features(f"{package_name}.{name}")
                else:
                    module_path = f"{package_name}.{name}"
                    try:
                        module = importlib.import_module(module_path)
                        for item_name in dir(module):
                            item = getattr(module, item_name)
                            if (
                                isinstance(item, type)
                                and issubclass(item, commands.Cog)
                                and item != commands.Cog
                            ):
                                category = getattr(
                                    item, "__cog_category__", item.__cog_name__
                                )
                                self.features[module_path] = {
                                    "class": item,
                                    "category": category,
                                    "description": getattr(
                                        item, "__cog_description__", ""
                                    ),
                                    "enabled": True,
                                }
                    except Exception as e:
                        logger.error(f"Failed to load module {module_path}: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to discover features in {package_name}: {str(e)}")

    async def load_discovered_features(self) -> bool:
        """Load all discovered features"""
        success = True
        loaded_features = []
        failed_features = []

        for module_path, feature in self.features.items():
            if feature["enabled"]:
                try:
                    await self.bot.load_extension(module_path)
                    self.loaded_modules[module_path] = True
                    loaded_features.append(feature["category"])
                except Exception as e:
                    success = False
                    self.loaded_modules[module_path] = False
                    failed_features.append(f"{feature['category']} ({str(e)})")

        # Log results once
        if loaded_features:
            logger.info(
                f"Successfully loaded {len(loaded_features)} features: {', '.join(loaded_features)}"
            )
        if failed_features:
            logger.error(
                f"Failed to load {len(failed_features)} features: {', '.join(failed_features)}"
            )

        return success

    async def reload_feature(self, module_path: str) -> bool:
        """Reload a specific feature"""
        try:
            if module_path in self.loaded_modules:
                await self.bot.reload_extension(module_path)
                logger.info(f"Reloaded feature: {module_path}")
                return True
            else:
                logger.warning(f"Feature not loaded: {module_path}")
                return False
        except Exception as e:
            logger.error(f"Failed to reload {module_path}: {str(e)}")
            return False

    async def unload_feature(self, module_path: str) -> bool:
        """Unload a specific feature"""
        try:
            if module_path in self.loaded_modules:
                await self.bot.unload_extension(module_path)
                del self.loaded_modules[module_path]
                logger.info(f"Unloaded feature: {module_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to unload {module_path}: {str(e)}")
            return False

    def get_loaded_features(self) -> Dict[str, Dict]:
        """Get information about all loaded features"""
        return {
            module_path: feature
            for module_path, feature in self.features.items()
            if self.loaded_modules.get(module_path, False)
        }

    def get_feature_status(self) -> Dict[str, bool]:
        """Get loading status of all features"""
        return self.loaded_modules.copy()
