
from datetime import datetime
import discord
from discord.ext import commands

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core import LIPOIC
    from .types.MemberApply import EventData


class MainEventsCog(discord.Cog):
    def __init__(self, bot: 'LIPOIC') -> None:
        self.bot = bot
        self.log = bot.log

    @discord.Cog.listener()
    async def on_ready(self):
        bot = self.bot
        if bot._uptime is not None:
            return

        bot._uptime = datetime.utcnow()
        bot.log.info(bot.user)
        bot._is_ready.set()

    # TODO watermelon watch this, new apply user event
    @discord.Cog.listener()
    async def on_new_apply(self, data: 'EventData'):
        print(data.email)

    # TODO watermelon watch this, link to the new apply server event
    @discord.Cog.listener()
    async def on_start_new_apply(self, data: str):
        print(data)

    @discord.Cog.listener()
    async def on_application_command_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        print(f"{type(error)}: {error}")
        # if isinstance(error, discord.ApplicationCommandInvokeError):
        #     embed = discord.Embed(title="發生錯誤!", description=f"Error:```{error}```", color=0xe74c3c)
        #     await ctx.respond(embed=embed)
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="發生錯誤!", description="你沒有權限執行指令", color=0xe74c3c
            )
            await ctx.respond(embed=embed)
