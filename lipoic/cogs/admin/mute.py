from typing import List
import discord
from discord import ApplicationContext, Option
from discord.ext import commands
import datetime

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core import LIPOIC


class MuteCog(discord.Cog):
    def __init__(self, bot: "LIPOIC"):
        self.bot = bot

    @commands.has_permissions(moderate_members=True)
    @discord.slash_command(description="Mute Member", guild_only=True)
    async def mute(
        self,
        ctx: ApplicationContext,
        member: Option(discord.Member, "輸入要禁言的成員(預設時間1分鐘)"),
        reason: Option(str, "Reason", default="無原因"),
        second: Option(int, "禁言的秒數", min_value=0, max_value=59, default=0),
        minute: Option(int, "禁言的分鐘數", min_value=0, max_value=59, default=0),
        hour: Option(int, "禁言的小時數", min_value=0, max_value=23, default=0),
        day: Option(int, "禁言的天數", min_value=0, max_value=6, default=0),
        week: Option(int, "禁言的週數", min_value=0, max_value=52, default=0),
    ):
        duration = datetime.timedelta(
            seconds=second, minutes=minute, hours=hour, days=day, weeks=week
        )
        if not duration:
            minute = 1
            duration = datetime.timedelta(minutes=1)
        await member.timeout_for(duration=duration, reason=reason)
        time_message: List[str] = []
        if week:
            time_message.append(f"{week}週")
        if day:
            time_message.append(f"{day}天")
        if hour:
            time_message.append(f"{hour}小時")
        if minute:
            time_message.append(f"{minute}分鐘")
        if second:
            time_message.append(f"{second}秒")
        embed = discord.Embed(
            title="禁言成功!", description=f"原因: {reason}\n持續時間: {' '.join(time_message)}"
        )
        await ctx.respond(embed=embed, ephemeral=True)

    @mute.error
    async def mute_error(self, ctx: ApplicationContext, error):
        embed = discord.Embed(
            title="禁言失敗!", description=f"Error:```{error}```", color=0xE74C3C
        )
        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(MuteCog(bot))
