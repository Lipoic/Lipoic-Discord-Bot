
from datetime import datetime
import discord
from discord.ext import commands

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from core import LIPOIC


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

    @discord.Cog.listener()
    async def on_application_command_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        print(f"{type(error)}: {error}")
        # if isinstance(error, discord.ApplicationCommandInvokeError):
        #     embed = discord.Embed(title="發生錯誤!", description=f"Error:```{error}```", color=0xe74c3c)
        #     await ctx.respond(embed=embed)
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(title="發生錯誤!", description="你沒有權限執行指令", color=0xe74c3c)
            await ctx.respond(embed=embed)
