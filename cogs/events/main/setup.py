
from datetime import datetime
from discord.ext import commands

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from core import LIPOIC


class SetUpCog(commands.Cog):
    def __init__(self, bot: 'LIPOIC') -> None:
        self.bot = bot
        self.log = bot.log

    @commands.Cog.listener()
    async def on_ready(self):
        bot = self.bot
        if bot._uptime is not None:
            return

        bot._uptime = datetime.utcnow()
        bot.log.info(bot.user)
        bot._is_ready.set()


def setup(bot: 'LIPOIC'):
    bot.add_cog(SetUpCog(bot))
