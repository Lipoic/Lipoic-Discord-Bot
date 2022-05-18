
from datetime import datetime
import discord
from discord.ext import commands

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from core import LIPOIC


class MainEventsCog(commands.Cog):
    def __init__(self, bot: 'LIPOIC') -> None:
        self.bot = bot
        self.log = bot.log

    @commands.Cog.listener()
    async def on_ready(self):
        bot = self.bot
        if bot._uptime is not None:
            return

        bot._uptime = datetime.utcnow()
        bot.log.info(bot.user)
        bot._is_ready.set()

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        print(type(error))
        if isinstance(error, discord.ApplicationCommandInvokeError):
            await ctx.respond("此命令不能在私人消息中使用")