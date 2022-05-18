import discord
from discord.ext import commands

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core import LIPOIC


class HelloCog(commands.Cog):
    def __init__(self, bot: 'LIPOIC'):
        self.bot = bot

    @discord.slash_command(description="Ping!", guild_only=True)
    async def ping(self, ctx: discord.ApplicationContext):
        await ctx.respond("Pong!")

    @discord.slash_command(description="Say Hello to Bot!", guild_only=True)
    async def hello(self, ctx: discord.ApplicationContext):
        await ctx.respond("Hello, World!")


def setup(bot: 'LIPOIC'):
    bot.add_cog(HelloCog(bot))
