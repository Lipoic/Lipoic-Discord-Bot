import platform

import rich
from main import __version__
from typing import Any, List, Optional, Union
import logging

import os
import discord
import asyncio


from .db import DB
from .events import MainEventsCog

__all__ = ["LIPOIC"]
log = logging.getLogger("lipoic")


class LIPOIC(discord.Bot):
    __version__ = __version__

    def __init__(self, *args, **kwargs):
        self._config = []

        kwargs["owner_ids"] = set(kwargs.get("owner_ids", set()))

        owner_id = kwargs.get("owner_id")
        if owner_id is not None:
            kwargs["owner_ids"].add(owner_id)

        kwargs["intents"] = kwargs.get("intents", discord.Intents.default())

        self.log = log
        self.db = DB(self)
        self.db.connect()
        self._uptime = None
        self.dev_user_ids: List[int] = set(kwargs.get("dev_user_ids", set()))

        super().__init__(*args, **kwargs)

        self._is_ready = asyncio.Event()

    def get_cog(self, name: str, /) -> Optional[discord.Cog]:
        cog = super().get_cog(name)
        assert cog is None or isinstance(cog, discord.Cog)
        return cog

    async def get_or_fetch_user(self, user_id: Union[int, str]) -> discord.User:
        """
        get or fetch user

        Parameters
        -----------
        user_id: Union[int, str]
            The ID of the user that should be retrieved.

        Raises
        -------
        Errors
            Please refer to `discord.Client.fetch_user`.

        Returns
        --------
        discord.User
            The user you requested.
        """
        if (user := self.get_user(int(user_id))) is not None:
            return user
        return await self.fetch_user(user_id)

    async def get_or_fetch_member(self, guild: discord.Guild, member_id: Union[int, str]):
        """
        get or fetch member

        Parameters
        -----------
        user_id: Union[int, str]
            The ID of the user that should be retrieved.

        Raises
        -------
        Errors
            Please refer to `discord.Client.fetch_member`.

        Returns
        --------
        discord.User
            The user you requested.
        """
        if (member := guild.get_member(int(member_id))) is not None:
            return member
        return await guild.fetch_member(guild, member_id)

    async def is_owner(self, user: Union[discord.User, discord.Member], /) -> bool:
        """
        has is_owner

        Parameters
        ----------
        user: Union[discord.User, discord.Member]

        Returns
        -------
        bool
        """
        return user.id in self.owner_ids

    def add_cog(self, cog: discord.Cog, /, *, override=False):
        if not isinstance(cog, discord.Cog):
            raise RuntimeError(
                f"The {cog.__class__.__name__} class is not a cog.",
                f"class in the {cog.__module__}"
            )

        self.log.info(
            f"load {cog.__class__.__name__} class in the {cog.__module__}",
        )

        super().add_cog(cog, override=override)

    def load_cog_dir(self, package_path: str, path: str, *, deep: bool = True):
        path = os.path.dirname(os.path.realpath(path)) if \
            os.path.isfile(path) else path

        for _ in os.listdir(path):
            fullpath = os.path.join(path, _)
            if os.path.isfile(fullpath) and _.endswith(".py") and _ != "__init__.py":
                self.load_extension(f"{package_path}.{_[:-3]}")
            elif deep and os.path.isdir(fullpath):
                self.load_cog_dir(f"{package_path}.{_}", fullpath)

    def run(self, *args: Any, **kwargs: Any):
        rich_output_message = ""
        rich_output_message += f"[red]python version: {platform.python_version()}[/red]\n"
        rich_output_message += f"[red]py-cord version: {discord.__version__}[/red]\n"
        rich_output_message += f"[red]LIPOIC version: {self.__version__}[/red]\n"

        self.load_extension("cogs.__init__")
        self.add_cog(MainEventsCog(self))
        super().run(*args, **kwargs)
