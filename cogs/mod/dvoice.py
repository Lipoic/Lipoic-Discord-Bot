
import discord


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core import LIPOIC


class DynamicVoiceCog(discord.Cog):
    def __init__(self, bot: 'LIPOIC') -> None:
        self.bot = bot
        self.dvc_dict = {}

    @discord.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState
    ):
        if after.channel and after.channel.id == 975755760032165888:  # Channel ID Just For Test
            try:
                dvc = self.dvc_dict[str(member.id)]
            except:
                dvc = await after.channel.category.create_voice_channel(name=f"{member.display_name}的頻道")
                self.dvc_dict[str(member.id)] = dvc
            await member.move_to(dvc)
        if before.channel and not before.channel.members and before.channel in list(self.dvc_dict.values()):
            await before.channel.delete()
            for i in self.dvc_dict:
                if self.dvc_dict[i] == before.channel:
                    del self.dvc_dict[i]
                    break


def setup(bot: 'LIPOIC'):
    bot.add_cog(DynamicVoiceCog(bot))
