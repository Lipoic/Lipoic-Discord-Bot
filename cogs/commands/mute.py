import discord
from discord.ext import commands
from discord import Embed, ApplicationContext, Option
from datetime import timedelta


class MuteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(mute_members=True)
    @discord.slash_command(description="Mute Member", guild_only=True)
    async def mute(
        self,
        ctx: ApplicationContext,
        member: Option(discord.Member, "輸入要禁言的成員(預設時間1分鐘)"),
        reason: Option(str, "Reason", default="無原因"),
        second: Option(int, "禁言的秒數", min_value=0, max_value=60, default=0),
        minute: Option(int, "禁言的分鐘數", min_value=0, max_value=60, default=1),
        hour: Option(int, "禁言的小時數", min_value=0, max_value=24, default=0),
        day: Option(int, "禁言的天數", min_value=0, max_value=7, default=0),
        week: Option(int, "禁言的週數", min_value=0, max_value=52, default=0)
    ):
        duration = timedelta(
            seconds=second, minutes=minute,
            hours=hour, days=day, weeks=week
        )
        await member.timeout_for(duration=duration, reason=reason)
        embed = Embed(title="禁言成功!", description=f"原因: {reason}")
        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(MuteCog(bot))
