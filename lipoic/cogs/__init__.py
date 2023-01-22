from typing import TYPE_CHECKING

import dotenv
import discord
from discord import ApplicationContext, Option

from lipoic import __config_path__, BaseCog
from lipoic.core.types.MemberApply import EventData


if TYPE_CHECKING:
    from core import LIPOIC


class DevCog(BaseCog, dev=True):
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
                selfIntro="test2",
                identity="學生",
                CV="test2",
                reason="test2",
                thoughts="test2",
                job="Discord Bot 開發部 - 開發工程師 (Python)",
                remark="test2",
                time="2022/12/31 下午 11:59:59",
                ID=16,
            ),
        )
        await ctx.respond("call apply successfully")


def setup(bot: "LIPOIC"):
    bot.add_cog(DevCog(bot))
    bot.load_cog_dir(__package__, __file__, deep=True)
