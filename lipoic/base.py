from typing import TYPE_CHECKING, Any, ClassVar, Type, TypeVar

import discord

if TYPE_CHECKING:
    from .core.bot import LIPOIC

__all__ = ("BaseCog",)

CogT = TypeVar("CogT", bound="BaseCog")


class BaseCogMeta(discord.CogMeta):
    __cog_dev__: bool

    def __new__(cls: Type[CogT], *args: Any, **kwargs: Any) -> CogT:
        name, base, attrs = args

        attrs["__cog_dev__"] = kwargs.pop("dev", False)

        return super().__new__(cls, name, base, attrs, **kwargs)


class BaseCog(discord.Cog, metaclass=BaseCogMeta):
    __cog_dev__: ClassVar[bool]

    def __init__(self, bot: "LIPOIC") -> None:
        self.bot = bot
        self.db = bot.db
        self.log = bot.log
