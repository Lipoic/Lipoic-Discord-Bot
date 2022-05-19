
import discord
import peewee


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

        if after.channel and after.channel.id == 976688759624056832:  # Channel ID Just For Test
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


def setup(bot: 'LIPOIC'):
    bot.add_cog(DynamicVoiceCog(bot))
