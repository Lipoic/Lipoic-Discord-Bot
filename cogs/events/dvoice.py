import discord
from discord.ext import commands


class DynamicVoiceCog(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.dvc_dict = {}

    @commands.Cog.listener()
    async def on_voice_state_update(self, 
                                    member: discord.Member, 
                                    before: discord.VoiceState, 
                                    after: discord.VoiceState):
        if not after.channel is None and after.channel.id == 975755760032165888: # Channel ID Just For Test
            try:
                dvc = self.dvc_dict[str(member.id)]
            except:
                dvc = await after.channel.category.create_voice_channel(name=f"{member.display_name}的頻道")
                self.dvc_dict[str(member.id)] = dvc
            await member.move_to(dvc)
        if not before.channel is None and not before.channel.members and before.channel in list(self.dvc_dict.values()):
            await before.channel.delete()
            for i in self.dvc_dict:
                if self.dvc_dict[i] == before.channel:
                    del self.dvc_dict[i]
                    break

def setup(bot):
    bot.add_cog(DynamicVoiceCog(bot))