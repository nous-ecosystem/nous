from discord import app_commands
from discord.ext import commands
import hashlib
import json
from typing import Dict, Optional
from src.utils.logger import logger
from src.database.manager import DatabaseManager
from sqlalchemy import Column, String, select
from src.database.models import CommandHash
import discord


class CommandSyncer:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = DatabaseManager()

    def _get_command_data(
        self, command: app_commands.Command | app_commands.Group
    ) -> dict:
        """Extract command data recursively, handling both commands and groups"""
        command_dict = {
            "name": command.name,
            "description": command.description,
        }

        # Handle regular commands
        if isinstance(command, app_commands.Command):
            command_dict["parameters"] = [
                {
                    "name": param.name,
                    "description": param.description,
                    "type": str(param.type),
                    "required": param.required,
                }
                for param in command.parameters
            ]

        # Handle command groups
        elif isinstance(command, app_commands.Group):
            command_dict["subcommands"] = [
                self._get_command_data(cmd) for cmd in command.commands
            ]

        return command_dict

    def _generate_command_hash(
        self, commands: list[app_commands.Command | app_commands.Group]
    ) -> str:
        """Generate a hash of the command tree for comparison"""
        command_data = []

        for cmd in sorted(commands, key=lambda x: x.name):
            command_data.append(self._get_command_data(cmd))

        command_json = json.dumps(command_data, sort_keys=True)
        return hashlib.sha256(command_json.encode()).hexdigest()

    async def _get_stored_hash(self, guild_id: Optional[str] = None) -> Optional[str]:
        """Get the stored command hash for the given guild"""
        async with self.db.get_session() as session:
            result = await session.execute(
                select(CommandHash).filter(
                    CommandHash.guild_id == (guild_id or "global")
                )
            )
            command_hash = result.scalar_one_or_none()
            return command_hash.command_hash if command_hash else None

    async def _store_hash(self, command_hash: str, guild_id: Optional[str] = None):
        """Store the command hash for the given guild"""
        async with self.db.get_session() as session:
            result = await session.execute(
                select(CommandHash).filter(
                    CommandHash.guild_id == (guild_id or "global")
                )
            )
            command_hash_obj = result.scalar_one_or_none()

            if command_hash_obj:
                command_hash_obj.command_hash = command_hash
            else:
                command_hash_obj = CommandHash(
                    guild_id=(guild_id or "global"), command_hash=command_hash
                )
                session.add(command_hash_obj)
            await session.commit()

    async def sync_commands(self, guild_id: Optional[str] = None) -> bool:
        """
        Sync commands only if they've changed
        Returns True if sync was performed, False if no sync was needed
        """
        try:
            # Get the command tree for the specified scope
            if guild_id:
                guild = self.bot.get_guild(int(guild_id))
                if not guild:
                    logger.error(f"Guild not found: {guild_id}")
                    return False
                commands = self.bot.tree.get_commands(guild=guild)
            else:
                commands = self.bot.tree.get_commands()

            # Generate hash of current commands
            current_hash = self._generate_command_hash(commands)
            stored_hash = await self._get_stored_hash(guild_id)

            # If hashes match, no sync needed
            if stored_hash == current_hash:
                logger.info(
                    f"Commands unchanged for {'guild ' + guild_id if guild_id else 'global'} - skipping sync"
                )
                return False

            # Sync commands with error handling
            try:
                if guild_id:
                    guild = self.bot.get_guild(int(guild_id))
                    if guild:
                        synced = await self.bot.tree.sync(guild=guild)
                        logger.info(
                            f"Synced {len(synced)} commands for guild {guild_id}"
                        )
                else:
                    synced = await self.bot.tree.sync()
                    logger.info(f"Synced {len(synced)} global commands")

                # Store new hash only after successful sync
                await self._store_hash(current_hash, guild_id)
                return True

            except discord.HTTPException as e:
                logger.error(f"Failed to sync commands: {e}")
                return False

        except Exception as e:
            logger.error(f"Error in sync_commands: {str(e)}")
            return False

    async def sync_all_guilds(self):
        """Sync commands for all guilds and global commands"""
        try:
            # Sync global commands first
            global_success = await self.sync_commands()
            logger.info(
                f"Global command sync {'successful' if global_success else 'not needed'}"
            )

            # Sync guild-specific commands
            for guild in self.bot.guilds:
                guild_success = await self.sync_commands(str(guild.id))
                logger.info(
                    f"Guild {guild.id} command sync {'successful' if guild_success else 'not needed'}"
                )

        except Exception as e:
            logger.error(f"Error syncing all commands: {str(e)}")
