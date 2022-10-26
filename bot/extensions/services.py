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


class Service:
    """
    Represents a service of UnB.
    """
    
    __slots__ = ("url", "fancy_name", "last_result", "last_time")

    def __init__(self, url: str, fancy_name: str) -> None:
        self.url = url
        self.fancy_name = fancy_name
        self.last_result = None
        self.last_time = discord.utils.utcnow()
        

class Services(commands.Cog):
    """
    A service checker from the UnB website.
    """

    def __init__(self, bot: UnBot) -> None:
        self.bot = bot
        self.services = [
            Service("https://aprender3.unb.br", "Aprender3"),
            Service("https://sigaa.unb.br/sigaa", "SIGAA"),
        ]

        self.check_services.start()

    async def check_service(self, service: Service) -> None:
        try:
            async with self.bot.session.get(service.url):
                is_active = True
        except asyncio.TimeoutError:
            is_active = False

        if service.last_result is None:
            service.last_result = is_active
            return

        if is_active is service.last_result:
            return

        service.last_result = is_active
        await self.send_service_status(service)        

    @discord.utils.cached_property
    def channel(self) -> discord.TextChannel:
        channel = self.bot.guild.get_channel(CHANNEL_ID)

        if not channel:
            raise Exception("Invalid service channel ID provided")

        assert isinstance(channel, discord.TextChannel)
        return channel

    @tasks.loop(minutes=5.0)
    async def check_services(self) -> None:
        for service in self.services:
            await self.check_service(service)

    @check_services.before_loop
    async def before_check_services(self) -> None:
        await self.bot.wait_until_ready()

    async def send_service_status(self, service: Service) -> None:
        if service.last_result:
            title = f"🟢 O {service.fancy_name} voltou ao ar!"
        else:
            title = f"🔴 O {service.fancy_name} caiu!"

        now = discord.utils.utcnow()

        delta = humanize.naturaldelta(now - service.last_time)
        message = f"Depois de **{delta}**!"

        embed = discord.Embed(title=title, description=message, color=0x008940)
        await self.channel.send(embed=embed)

        service.last_time = now


async def setup(bot: UnBot):
    await bot.add_cog(Services(bot))
