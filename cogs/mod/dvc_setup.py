from typing import List
import discord
from discord import ApplicationContext, Option, OptionChoice, Embed

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core import LIPOIC


class DynamicVoiceSetupCog(discord.Cog):
    def __init__(self, bot: 'LIPOIC'):
        self.bot = bot

    @discord.slash_command(description="Dynamic Voice Setting", guild_only=True)
    async def dvc(
        self,
        ctx: ApplicationContext,
        mode: Option(str, "選擇模式", choices=[OptionChoice("help"), OptionChoice("fix")])
    ):
        Dvc = self.bot.db.Dvc
        if mode == "help":
            embed = Embed(
                title="教學!", description=f"進入<#{self.bot.dvc_id}>語音後，就會自動創建自己的語音頻道"
            )
        elif mode == "fix":
            dvc = await self.bot.get_or_fetch_channel(self.bot.dvc_id)
            for channel in dvc.category.channels:
                if not channel.members and channel.id in [id.channel_id for id in Dvc.select()]:
                    await channel.delete()
                    Dvc.delete().where(Dvc.channel_id == channel.id).execute()
            embed = Embed(
                title="修復成功!", color=0x2ecc71
            )
        await ctx.respond(embed=embed, ephemeral=True)

    @dvc.error
    async def mute_error(self, ctx: ApplicationContext, error):
        embed = discord.Embed(
            title="失敗!", description=f"Error:```{error}```", color=0xe74c3c
        )
        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot: 'LIPOIC'):
    bot.add_cog(DynamicVoiceSetupCog(bot))
