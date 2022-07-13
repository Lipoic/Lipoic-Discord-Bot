import os
from typing import TYPE_CHECKING

import discord
from discord import ApplicationContext, Option
import dotenv

from lipoic.core.types.MemberApply import EventData
from lipoic import __config_path__


if TYPE_CHECKING:
    from core import LIPOIC


class DevCog(discord.Cog):
    def __init__(self, bot: "LIPOIC"):
        self.bot = bot

    @discord.slash_command(description="dev reload command", guild_only=True)
    async def reload(self, ctx: ApplicationContext):
        self.bot.load_cog_dir(__package__, __file__, deep=True, type="reload")
        dotenv.load_dotenv(dotenv_path=__config_path__ / ".env", override=True)
        self.bot.load_config()
        await ctx.respond("reload", ephemeral=True)

    @discord.slash_command(description="call_apply", guild_only=True)
    async def test_apply(
        self, ctx: ApplicationContext, test_email: Option(str, "申請者 email")
    ):
        self.bot.dispatch(
            "new_apply",
            EventData(
                email=test_email,
                selfIntro="test",
                identity="學生",
                CV="test",
                reason="test",
                thoughts="test",
                jobs=["資訊 - 前端 (Vue.js)"],
                remark="test",
                time="2022/7/1 下午 2:22:49",
                ID=10,
            ),
        )
        await ctx.respond("call apply")


def setup(bot: "LIPOIC"):
    if bot.debug:
        bot.add_cog(DevCog(bot))
    bot.load_cog_dir(__package__, __file__, deep=True)
