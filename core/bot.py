import json
import yaml
import platform
import aiohttp
from .types.MemberApply import EventData

from main import __version__
from typing import Any, Dict, List, Callable, Coroutine, Literal, Optional, Union
import logging

import os
import discord
import asyncio


from .db import DB
from .events import MainEventsCog

__all__ = ["LIPOIC"]
log = logging.getLogger("lipoic")
loadCogType = Literal["load", "reload", "unload"]
CoreFuncType = Callable[..., Coroutine[Any, Any, Any]]


class LIPOIC(discord.Bot):
    __version__ = __version__

    def __init__(self, *args, **kwargs):
        self._config = []
        self.lipoic_events: Dict[str, CoreFuncType] = {}

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
        self.configs = {
            'newApplyServerToken': os.getenv('NEW_APPLY_SERVER_TOKEN'),
        }

        # config setting
        with open("config.yml", "r", encoding="utf8") as config_yaml:
            config = yaml.load(config_yaml, yaml.Loader)
        self.log.info("load config.yml is complete")
        # print(config)
        self.dvc_ids: List[int] = config['dvc_id']
        self.member_role_id: int = config['member_role_id']
        self.apply_channel_id: int = config['apply_channel_id']
        self.job_role: dict = config['job_role']

        super().__init__(*args, **kwargs)

        self._is_ready = asyncio.Event()

    def get_cog(self, name: str, /) -> Optional[discord.Cog]:
        cog = super().get_cog(name)
        assert cog is None or isinstance(cog, discord.Cog)
        return cog

    def emit(self, event_name: str, *args: Any, **kwargs: Any) -> None:
        for event in self.lipoic_events.get(event_name, []):
            self.lipoic_schedule_event(event, event_name, *args, **kwargs)

    def lipoic_schedule_event(
        self,
        func: CoreFuncType,
        event_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> asyncio.Task:
        return asyncio.create_task(self._run_event(func, event_name, *args, **kwargs), name=f"lipoic: {event_name}")

    def addEventListener(self, func: CoreFuncType, event_name: Optional[str] = None) -> None:
        event_name = event_name or func.__name__

        if event_name in self.lipoic_events:
            self.lipoic_events[event_name].append(func)
        else:
            self.emit("newListener", event_name, event_name=event_name)
            self.lipoic_events[event_name] = [func]

    def on(self, func: CoreFuncType, event_name: Optional[str] = None) -> None:
        return self.addEventListener(func, event_name)

    def removeEventListener(self, func: CoreFuncType, event_name: Optional[str] = None) -> None:
        event_name = event_name or func.__name__

        if event_name in self.extra_events:
            try:
                self.extra_events[event_name].remove(func)
            except ValueError:
                ...

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
        if (user := self.get_user(user_id := int(user_id))) is not None:
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
        if (member := guild.get_member(member_id := int(member_id))) is not None:
            return member
        return await guild.fetch_member(guild, member_id)

    async def get_or_fetch_channel(self, channel_id: Union[int, str]):
        if (channel := self.get_channel(channel_id := int(channel_id))) is not None:
            return channel
        return await self.fetch_channel(channel_id)

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

    def load_cog_dir(self, package_path: str, path: str, *, deep: bool = True, type: loadCogType = "load"):
        switch = {
            "load": self.load_extension,
            "unload": self.unload_extension,
            "reload": self.reload_extension
        }
        callFunc = switch.get(type)
        if callFunc is None:
            raise ValueError("type must be load, unload or reload")
        path = os.path.dirname(os.path.realpath(path)) if \
            os.path.isfile(path) else path

        for _ in os.listdir(path):
            fullpath = os.path.join(path, _)
            if os.path.isfile(fullpath) and _.endswith(".py") and _ != "__init__.py":
                callFunc(f"{package_path}.{_[:-3]}")
            elif deep and os.path.isdir(fullpath):
                self.load_cog_dir(f"{package_path}.{_}", fullpath, type=type)

    async def getNewApply(self):
        await self._is_ready.wait()
        while not self.is_closed():
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.ws_connect(
                        'ws://lipoic.a102009102009.repl.co',
                        timeout=30,
                        autoclose=False,
                        max_msg_size=0,
                    ) as ws:
                        async def getMsg():
                            data = await ws.receive()
                            msg = data.data
                            try:
                                msg = json.loads(msg)
                            except:
                                ...
                            return (data.type, msg)
                        while True:
                            _type, msg = await getMsg()

                            if _type in [aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR]:
                                break
                            if not isinstance(msg, dict):
                                continue
                            op = msg.get('op', -1)
                            msgType = msg.get('type', None)
                            if op == 1:
                                self.log.debug(
                                    '[new-apply-server] check Heartbeat'
                                )
                                continue
                            if op == 0:
                                if msgType == 'READY':
                                    await ws.send_str(json.dumps({
                                        'op': 5,
                                        'authorization': self.configs['newApplyServerToken']
                                    }))
                                    continue
                                if msgType == 'START':
                                    self.dispatch('start_new_apply')
                                    continue
                                if msgType == 'NEW_APPLY':
                                    self.dispatch(
                                        'new_apply',
                                        EventData(**msg.get('data'))
                                    )
                                    self.log.debug(
                                        '[new-apply-server] get new apply'
                                    )
                                    continue
            except Exception as e:
                self.log.error(e)

    def run(self, *args: Any, **kwargs: Any):
        rich_output_message = ""
        rich_output_message += f"[red]python version: {platform.python_version()}[/red]\n"
        rich_output_message += f"[red]py-cord version: {discord.__version__}[/red]\n"
        rich_output_message += f"[red]LIPOIC version: {self.__version__}[/red]\n"

        self.load_extension("cogs.__init__")
        self.add_cog(MainEventsCog(self))

        self.loop.create_task(self.getNewApply())

        super().run(*args, **kwargs)
