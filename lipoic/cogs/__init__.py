from typing import TYPE_CHECKING

from discord import ApplicationContext


if TYPE_CHECKING:
    from core import LIPOIC


def setup(bot: "LIPOIC"):
    if bot.debug:

        @bot.command()
        async def reload(ctx: ApplicationContext):
            bot.load_cog_dir(__package__, __file__, deep=True, type="reload")
            await ctx.respond("reload")

    bot.load_cog_dir(__package__, __file__, deep=True)
