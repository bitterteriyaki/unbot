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

import asyncio

import discord
import humanize
from discord.ext import commands, tasks # type: ignore

from bot.core import UnBot


CHANNEL_ID = 991129043011383387


class Services(commands.Cog):
    """
    A service checker from the UnB website.
    """

    def __init__(self, bot: UnBot) -> None:
        self.bot = bot
        self.service_url = "https://aprender3.unb.br"

        self.last_result = None
        self.last_time = discord.utils.utcnow()

        self.check_services.start()

    @discord.utils.cached_property
    def channel(self) -> discord.TextChannel:
        channel = self.bot.guild.get_channel(CHANNEL_ID)

        if not channel:
            raise Exception("Invalid service channel ID provided")

        assert isinstance(channel, discord.TextChannel)
        return channel

    @tasks.loop(minutes=5.0)
    async def check_services(self) -> None:
        try:
            async with self.bot.session.get(self.service_url):
                is_active = True
        except asyncio.TimeoutError:
            is_active = False

        if is_active is self.last_result:
            return

        self.last_result = is_active
        await self.send_service_status()

    @check_services.before_loop
    async def before_check_services(self) -> None:
        await self.bot.wait_until_ready()

    async def send_service_status(self) -> None:
        if self.last_result is None:
            return

        if self.last_result:
            title = "🟢 O Aprender3 voltou ao ar!"
        else:
            title = "🔴 O Aprender3 caiu!"

        now = discord.utils.utcnow()

        delta = humanize.naturaldelta(now - self.last_time)
        message = f"Depois de **{delta}**!"

        embed = discord.Embed(title=title, description=message, color=0x008940)
        await self.channel.send(embed=embed)

        self.last_time = now


async def setup(bot: UnBot):
    await bot.add_cog(Services(bot))
