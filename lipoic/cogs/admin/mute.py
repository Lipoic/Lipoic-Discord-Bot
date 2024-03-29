import datetime
import re
from typing import TYPE_CHECKING

import discord
from discord.ext import commands
from discord import ApplicationContext, Option

from lipoic import BaseCog

if TYPE_CHECKING:
    from core import LIPOIC


class MuteCog(BaseCog):
    def __init__(self, bot: "LIPOIC") -> None:
        super().__init__(bot)
        self.duration_regex = re.compile(r"(\d+)([dhms]*)")
        self.duration_maps = {"d": "days", "h": "hours", "m": "minutes", "s": "seconds"}
        self.tz = datetime.timezone(datetime.timedelta(hours=+8))

    @commands.has_permissions(moderate_members=True)
    @discord.slash_command(description="禁言成員(預設時間5分鐘)", guild_only=True)
    async def mute(
        self,
        ctx: ApplicationContext,
        member: Option(discord.Member, "輸入要禁言的成員"),
        duration: Option(
            str, "持續時間(和until衝突)，格式: 天d時h分m秒s，例子: 1d5h10m, 30m", required=False
        ),
        until: Option(
            str,
            "直到某個時間點(和duration衝突，以UTF+8時區為主)，格式: 年-月-日 時:分:秒(24小時制)，例子: 2022-04-01 15:30:20, 03-04 20:00",  # noqa
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
            match = re.findall(self.duration_regex, duration)
            delta = datetime.timedelta()
            for num, unit in match:
                delta += datetime.timedelta(**{self.duration_maps[unit]: int(num)})

        elif until:
            now = datetime.datetime.now(self.tz)
            year = now.year
            month = now.month
            day = now.day
            # 切分日期和時間
            untils = until.split(" ")
            if len(untils) == 2:
                date = untils[0]
                time = untils[1]
                # 切分年月日
                dates = date.split("-")
                dates_len = len(dates)
                if dates_len == 3:
                    year, month, day = map(int, dates)
                elif dates_len == 2:
                    month, day = map(int, dates)
                else:
                    day = map(int, dates)
            elif len(untils) == 1:
                time = untils[0]
            else:
                return await ctx.respond(
                    embed=discord.Embed(
                        title="禁言失敗!", description="未知的時間格式!", color=0xE74C3C
                    ),
                    ephemeral=True,
                )

            hour = minute = second = 0
            # 切分時分秒
            times = time.split(":")
            if len(times) == 3:
                hour, minute, second = map(int, times)
            elif len(times) == 2:
                hour, minute = map(int, times)
            else:
                return await ctx.respond(
                    embed=discord.Embed(
                        title="禁言失敗!", description="未知的時間格式!", color=0xE74C3C
                    ),
                    ephemeral=True,
                )
            delta = (
                datetime.datetime(
                    year, month, day, hour, minute, second, tzinfo=self.tz
                )
                - now
            )
            if delta.total_seconds() <= 0:
                return await ctx.respond(
                    embed=discord.Embed(
                        title="禁言失敗!", description="結束時間不能在過去!", color=0xE74C3C
                    ),
                    ephemeral=True,
                )
        else:
            delta = datetime.timedelta(minutes=5)

        if delta.total_seconds() > 2332800:  # 若禁言時間超過27天(2,332,800秒)
            return await ctx.respond(
                embed=discord.Embed(
                    title="禁言失敗!", description="若禁言時間不能超過27天!", color=0xE74C3C
                ),
                ephemeral=True,
            )

        days = delta.days
        hours, r = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(r, 60)

        await member.timeout_for(delta, reason=reason)
        embed = discord.Embed(
            title="禁言成功!",
            description=f"原因: {reason}\n時間: {days}天{hours}時{minutes}分{seconds}秒",
        )
        await ctx.respond(embed=embed, ephemeral=True)

    @mute.error
    async def mute_error(self, ctx: ApplicationContext, error):
        embed = discord.Embed(
            title="禁言失敗!", description=f"Error:```{error}```", color=0xE74C3C
        )
        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot: "LIPOIC"):
    bot.add_cog(MuteCog(bot))
