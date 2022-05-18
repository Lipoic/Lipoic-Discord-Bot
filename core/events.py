
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
    async def on_command_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        print(ctx.locale)
        if isinstance(error, commands.errors.NoPrivateMessage):
            await ctx.respond("此命令不能在私人消息中使用")
        elif isinstance(error, commands.errors.CommandOnCooldown):
            await ctx.respond(f"指令冷卻{error.retry_after:.2f}")
        elif isinstance(error, commands.errors.CommandNotFound):
            await ctx.respond("🧐 查無指令 🧐")
        elif isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.respond(f"🤔 缺少參數! 🤔\n{ctx.command.__doc__ or ''}")
        elif isinstance(error, commands.errors.MissingPermissions):
            await ctx.respond("你沒有權限!!")
        elif isinstance(error, commands.errors.NotOwner):
            await ctx.respond("你沒有權限!")
        elif isinstance(error, commands.errors.CheckAnyFailure):
            await ctx.respond("你沒有權限!")
        else:
            self.bot.log.error(f"error: {type(error).__name__, error}")
