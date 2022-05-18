
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from core import LIPOIC


def setup(bot: 'LIPOIC'):
    bot.load_cog_dir(__package__, __file__, deep=True)
