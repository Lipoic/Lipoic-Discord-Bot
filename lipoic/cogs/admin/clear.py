from typing import TYPE_CHECKING

import discord
from discord.ext import commands
from discord import Embed, ApplicationContext, Option

from lipoic import BaseCog

if TYPE_CHECKING:
    from core import LIPOIC


class ClearCog(BaseCog):
    @commands.has_permissions(manage_messages=True)
    @discord.slash_command(description="Delete Message", guild_only=True)
    async def delete(
        self,
        ctx: ApplicationContext,
        message_id: Option(str, "輸入要刪除的訊息ID"),
        reason: Option(str, "Reason", default="無原因"),
    ):
        message: discord.Message = await ctx.fetch_message(int(message_id))
        await message.delete(reason=reason)
        embed = Embed(title="訊息刪除成功!", description=f"原因: {reason}")
        embed.set_author(name=message.author, icon_url=message.author.avatar.url)
        await ctx.respond(embed=embed, ephemeral=True)

    @commands.has_permissions(manage_messages=True)
    @discord.slash_command(description="Delete Many Messages", guild_only=True)
    async def purge(
        self,
        ctx: ApplicationContext,
        count: Option(int, "輸入要刪除的訊息數量", min_value=1, max_value=512),
        reason: Option(str, "Reason", default="無原因"),
        member: Option(discord.Member, "要刪除的成員訊息", default=None),
        before: Option(str, "刪除這則訊息以前的訊息(請輸入訊息ID)", default=None),
        after: Option(str, "刪除以這則訊息以後的訊息(請輸入訊息ID)", default=None),
    ):
        if before and after:
            embed = Embed(
                title="錯誤!", description="`before` 和 `after` 選項不得同時出現", color=0xE74C3C
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return
        elif before:
            before: discord.Message = await ctx.fetch_message(int(before))
        elif after:
            after: discord.Message = await ctx.fetch_message(int(after))

        def del_check(message: discord.Message):
            return message.author == member or not member

        del_message = await ctx.channel.purge(
            limit=count, check=del_check, before=before, after=after
        )
        embed = Embed(
            title=f"成功刪除了`{len(del_message)}`則訊息!", description=f"原因: {reason}"
        )
        await ctx.respond(embed=embed, ephemeral=True)

    @purge.error
    async def purge_error(self, ctx: ApplicationContext, error):
        embed = discord.Embed(
            title="刪除失敗!", description=f"Error:```{error}```", color=0xE74C3C
        )
        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot: "LIPOIC"):
    bot.add_cog(ClearCog(bot))
