import discord
from discord.ext import commands


class DynamicVoiceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dvc_dict = {}

    @commands.Cog.listener()
    async def on_voice_state_update(self, 
                                    member: discord.Member, 
                                    before: discord.VoiceState, 
                                    after: discord.VoiceState):
        if after.channel and after.channel.id == 975755760032165888: # Channel ID Just For Test
            try:
                dvc = self.dvc_dict[str(member.id)]
            except:
                dvc = await after.channel.category.create_voice_channel(name=f"{member.display_name}的頻道")
                self.dvc_dict[str(member.id)] = dvc
            await member.move_to(dvc)
        if (before.channel and # if before channel != None
            not before.channel.members and # if before channel's members == None
            before.channel in list(self.dvc_dict.values())): # if before channel in dvc temp dict
            await before.channel.delete()
            for i in self.dvc_dict: # delete before channel in dvc temp dict
                if self.dvc_dict[i] == before.channel:
                    del self.dvc_dict[i]
                    break

def setup(bot):
    bot.add_cog(DynamicVoiceCog(bot))