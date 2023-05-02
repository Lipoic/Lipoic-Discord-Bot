import datetime
import re
from typing import List, TYPE_CHECKING

import discord
from discord.ext import commands
from discord import ApplicationContext, Option

from lipoic import BaseCog

if TYPE_CHECKING:
    from core import LIPOIC


class MuteCog(BaseCog):
    @commands.has_permissions(moderate_members=True)
    @discord.slash_command(description="Mute Member", guild_only=True)
    async def mute(
        self,
        ctx: ApplicationContext,
        member: Option(discord.Member, "輸入要禁言的成員(預設時間5分鐘)"),
        duration: Option(
            str, "持續時間(和until衝突)，格式: [數字][d/m/h/s]...，例子: 1d5h10m, 30m", required=False
        ),
        until: Option(
            str,
            "直到某個時間點(和duration衝突)，格式: yyyy-mm-dd hh:mm:ss，例子: 2022-04-01 15:30:20, 03-04 20:00",  # noqa
            required=False,
        ),
        reason: Option(str, "Reason", default="無原因"),
    ):
        if duration and until:
            return await ctx.respond(
                embed=discord.Embed(
                    title="禁言失敗!", description="duration和until參數不可同時出現!", color=0xE74C3C
                ),
                ephemeral=True,
            )

        if duration:
            match = re.findall(r"(\d+)([a-z]*)", duration)
            delta = datetime.timedelta()
            for num, unit in match:
                num = int(num)
                if unit == "d":
                    delta += datetime.timedelta(days=num)
                elif unit == "h":
                    delta += datetime.timedelta(hours=num)
                elif unit == "m":
                    delta += datetime.timedelta(minutes=num)
                elif unit == "s":
                    delta += datetime.timedelta(seconds=num)
        elif until:
            now = datetime.datetime.now()

            date, time = until.split(" ")
            year = now.year
            month = now.month
            day = now.day
            year, month, day = map(int, date.split("-"))

            hour = 0
            minute = 0
            second = 0
            hour, minute, second = map(int, time.split(":"))

            delta = datetime.datetime(year, month, day, hour, minute, second) - now
        else:
            delta = datetime.timedelta(minutes=5)

        await member.timeout_for(delta, reason=reason)
        embed = discord.Embed(title="禁言成功!", description=f"原因: {reason}\n時間: {delta}")
        await ctx.respond(embed=embed, ephemeral=True)

    @mute.error
    async def mute_error(self, ctx: ApplicationContext, error):
        embed = discord.Embed(
            title="禁言失敗!", description=f"Error:```{error}```", color=0xE74C3C
        )
        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot: "LIPOIC"):
    bot.add_cog(MuteCog(bot))
