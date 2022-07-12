from typing import TYPE_CHECKING, Any, Type, TypeVar

import discord

if TYPE_CHECKING:
    from .core.bot import LIPOIC

__all__ = ("BaseCog",)

CogT = TypeVar("CogT", bound="BaseCog")


class BaseCog(discord.Cog):
    __cog_dev__: bool

    def __init__(self, bot: "LIPOIC") -> None:
        self.bot = bot
        self.db = bot.db
        self.log = bot.log

    def __new__(cls: Type[CogT], *args: Any, **kwargs: Any) -> CogT:
        dev = kwargs.pop("dev", False)

        new_cls = super().__new__(cls, *args, **kwargs)

        new_cls.__cog_dev__ = dev

        return new_cls

    @property
    def dev(self) -> bool:
        return self.__cog_dev__
