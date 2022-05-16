import discord
from discord.ext import commands

class DvoiceCog(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_voice_stats_update(self, 
                                    member: discord.Member, 
                                    before: discord.VoiceState, 
                                    after: discord.VoiceState):
        if after.channel.id == 942291362861170699: #! For Test
            await after.channel.category.create_voice_channel(name=member)
        
        if not before.channel.members:
            await before.channel.delete()

def setup(bot):
    bot.add_cog(DvoiceCog(bot))