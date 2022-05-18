
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from core import LIPOIC


def loadCommands(bot: 'LIPOIC'):
    bot.load_extension(".commands.__init__", package=__package__)


def loadEvents(bot: 'LIPOIC'):
    bot.load_extension(".events.__init__", package=__package__)


def loadAll(bot: 'LIPOIC'):
    loadCommands(bot)
    loadEvents(bot)
