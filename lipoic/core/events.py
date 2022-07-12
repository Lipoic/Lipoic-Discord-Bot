from datetime import datetime
import discord
from discord.ext import commands

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core import LIPOIC
    from .types.MemberApply import EventData


class MainEventsCog(discord.Cog):
    def __init__(self, bot: "LIPOIC") -> None:
        self.bot = bot
        self.log = bot.log

    @discord.Cog.listener()
    async def on_ready(self):
        bot = self.bot
        if bot._uptime is not None:
            return

        bot._uptime = datetime.utcnow()
        bot.log.info(f"[cyan]{bot.user}[/cyan]")
        bot._is_ready.set()

    # TODO watermelon watch this, new apply user event
    @discord.Cog.listener()
    async def on_new_apply(self, data: "EventData"):
        print(data.time)

    # TODO watermelon watch this, link to the new apply server event
    @discord.Cog.listener()
    async def on_start_new_apply(self):
        print("start")

    @discord.Cog.listener()
    async def on_application_command_error(
        self, ctx: discord.ApplicationContext, error: discord.DiscordException
    ):
        print(f"{type(error)}: {error}")
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="發生錯誤!", description="你沒有權限執行指令", color=0xE74C3C
            )
            await ctx.respond(embed=embed)
