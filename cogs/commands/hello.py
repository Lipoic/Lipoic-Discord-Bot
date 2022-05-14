from discord.ext import commands


class helloCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hello(self, ctx: commands.Context):
        await ctx.reply("Hello, World!")
        