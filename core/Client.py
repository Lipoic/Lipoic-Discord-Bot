

import logging
import datetime
import os
from pathlib import Path
from typing import List, Optional


import discord
import pkg_resources
from discord import app_commands
from dotenv import load_dotenv


class Client(discord.Client):
    MY_GUILD = discord.Object(id=0)

    def __init__(
        self, *,
        application_id: int,
        log: Optional[logging.Logger] = None,
        intents: Optional[discord.Intents] = None
    ):
        """setup"""
        load_dotenv(dotenv_path=Path(os.path.abspath(".")+"\\.env"))

        super().__init__(
            application_id=application_id,
            case_insensitive=True,
            owner_ids=self.owners, intents=self.Intents,
            allowed_mentions=discord.AllowedMentions(
                roles=False, users=True, everyone=False
            ),
        )

        strOwners = os.getenv("owners", None)

        # 設定 所有者
        self.owners = [
            int(owner)for owner in strOwners.split(",")
        ] if strOwners is not None else []

        # 需要加載的cog資料夾名
        self.__cogs_file: List[str] = ["__init__"]
        # 開機時間
        self.start_time = datetime.datetime.utcnow()
        # 日誌
        self.log = log or logging.getLogger()
        # 權限意圖
        self.Intents = intents or discord.Intents()

        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=self.MY_GUILD)
        await self.tree.sync(guild=self.MY_GUILD)

    def run(
        self,
        token: Optional[str] = None,
        version: Optional[str] = None
    ):
        """執行"""
        self.__version__ = pkg_resources.parse_version(
            "1.0.0" if version is None else version
        )
        try:
            super().run(os.getenv("TOKEN", token), reconnect=True)
        except discord.LoginFailure:
            raise Exception("請於 https://www.discordapp.com/developers 申請Bot")

    # event
    async def on_ready(self):
        """執行始初化/BOT開機呼叫"""
        print(self.user)
