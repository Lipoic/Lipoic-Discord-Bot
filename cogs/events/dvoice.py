import discord
from discord.ext import commands

class DynamicVoiceCog(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.channel_map = {}
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, 
                                    member: discord.Member, 
                                    before: discord.VoiceState, 
                                    after: discord.VoiceState):

        if not after is None and after.channel.id == 975755760032165888: #! For Test
            channel = await after.channel.category.create_voice_channel(name=str(member))
            await member.move_to(channel)
            self.channel_map[member.id] = channel.id
        
        if not before is None and not before.channel.members and before.channel.id != 975755760032165888:
            await before.channel.delete()

def setup(bot):
    bot.add_cog(DynamicVoiceCog(bot))