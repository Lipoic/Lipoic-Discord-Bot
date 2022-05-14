from discord.ext import commands
from discord.ext.commands import Context

class helloCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hello(self, ctx: Context):
        await ctx.reply("Hello, World!")
        