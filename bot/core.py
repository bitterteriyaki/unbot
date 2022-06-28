"""
Copyright (C) 2022  kyomi

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import aiohttp
import discord
from discord.ext import commands


__all__ = ("UnBot",)


GUILD_ID = 988618358029168690


class UnBot(commands.Bot):
    """
    Bot for information about UnB.
    """

    def __init__(self) -> None:
        intents = discord.Intents.all()
        super().__init__(command_prefix="?", intents=intents)

        self.is_first_launch = True

    @discord.utils.cached_property
    def guild(self) -> discord.Guild:
        guild = self.get_guild(GUILD_ID)

        if not guild:
            raise Exception("Invalid guild ID provided")

        return guild

    async def on_ready(self):
        if self.is_first_launch:
            self.is_first_launch = False

            print(f"Online with {len(self.users)} users")

    async def setup_hook(self) -> None:
        timeout = aiohttp.ClientTimeout(total=10)
        self.session = aiohttp.ClientSession(timeout=timeout)

        await self.load_extension("bot.extensions.services")

    async def close(self) -> None:
        await self.session.close()
        await super().close()
