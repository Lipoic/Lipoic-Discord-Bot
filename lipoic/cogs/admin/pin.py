from typing import TYPE_CHECKING

import discord
from discord import ApplicationContext, Option, Embed, Member

from lipoic import BaseCog

if TYPE_CHECKING:
    from core import LIPOIC


class PinCog(BaseCog):
    @discord.slash_command(description="Pin Message", guild_only=True)
    async def pin(
        self,
        ctx: ApplicationContext,
        message_id: Option(str, "輸入要釘選的訊息ID"),
        reason: Option(str, "Reason", default="無原因"),
    ):
        member_role = ctx.guild.get_role(self.bot.member_role_id)

        async def member_check(member: Member):
            return member_role in member.roles

        if not await member_check(ctx.author):
            return await ctx.respond(
                embed=Embed(title="釘選失敗!", description="您沒有權限", color=0xE74C3C),
                ephemeral=True,
            )

        message: discord.Message = await ctx.fetch_message(int(message_id))
        await message.pin(reason=reason)
        embed = Embed(
            title="訊息釘選成功!", description=f"[點擊跳至訊息]({message.jump_url})\n原因: {reason}"
        )
        embed.set_author(name=message.author, icon_url=message.author.avatar.url)
        await ctx.respond(embed=embed)

    @pin.error
    async def mute_error(self, ctx: ApplicationContext, error):
        embed = Embed(title="釘選失敗!", description=f"Error:```{error}```", color=0xE74C3C)
        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot: "LIPOIC"):
    bot.add_cog(PinCog(bot))
