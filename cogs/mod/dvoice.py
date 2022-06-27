
import discord
import peewee
from discord import ApplicationContext, Option, OptionChoice, Embed


from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from core import DvcType
    from core import LIPOIC


class DynamicVoiceCog(discord.Cog):
    def __init__(self, bot: 'LIPOIC') -> None:
        self.bot = bot

    @discord.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState
    ):
        Dvc = self.bot.db.Dvc

        if after.channel and after.channel.id in self.bot.dvc_ids:
            try:
                data: DvcType = Dvc.get(Dvc.user_id == member.id)
                channel = await self.bot.get_or_fetch_channel(data.channel_id)
            except Dvc.DoesNotExist:
                dvcChannel = await after.channel.category.create_voice_channel(name=f"{member.display_name}的頻道")
                channel = dvcChannel
                try:
                    Dvc.insert(
                        user_id=member.id,
                        channel_id=channel.id
                    ).execute()
                except peewee.InterfaceError:
                    ...
            await member.move_to(channel)

        if before.channel and not before.channel.members:
            if Dvc.delete().where(Dvc.channel_id == before.channel.id).execute():
                await before.channel.delete()

    @discord.slash_command(description="Dynamic Voice Setting", guild_only=True)
    async def dvc(
        self,
        ctx: ApplicationContext,
        mode: Option(str, "選擇模式", choices=[
                     OptionChoice("help"), OptionChoice("fix")])
    ):
        Dvc = self.bot.db.Dvc
        if mode == "help":
            dvcChannels = "\n".join([
                f"<#{id}>" for id in filter(lambda _: _ in [_.id for _ in ctx.guild.channels], self.bot.dvc_ids)
            ])
            embed = Embed(
                title="教學!",
                description=f"進入 {dvcChannels} 語音後，就會自動創建自己的語音頻道"
            )
        elif mode == "fix":
            dvc = await self.bot.get_or_fetch_channel(self.bot.dvc_ids)
            for channel in dvc.category.channels:
                if not channel.members and Dvc.delete().where(Dvc.channel_id == channel.id).execute():
                    await channel.delete()
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
    bot.add_cog(DynamicVoiceCog(bot))
