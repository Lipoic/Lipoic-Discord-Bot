from typing import List
import discord
from discord import ApplicationContext, Option, Embed
from discord.ext import commands
import datetime


class PinCog(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_role(804319904286507068)  # Role ID Just for Test
    @discord.slash_command(description="Pin Message", guild_only=True)
    async def pin(
        self,
        ctx: ApplicationContext,
        message_id: Option(str, "輸入要刪除的訊息ID"),
        reason: Option(str, "Reason", default="無原因")
    ):
        message: discord.Message = await ctx.fetch_message(int(message_id))
        await message.pin(reason=reason)
        embed = Embed(title="訊息釘選成功!", description=f"[點擊跳至訊息]({message.jump_url})\n原因: {reason}")
        embed.set_author(name=message.author,
                         icon_url=message.author.avatar.url)
        await ctx.respond(embed=embed)

    @pin.error
    async def mute_error(self, ctx: ApplicationContext, error):
        embed = discord.Embed(
            title="釘選失敗!", description=f"Error:```{error}```", color=0xe74c3c
        )
        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(PinCog(bot))
