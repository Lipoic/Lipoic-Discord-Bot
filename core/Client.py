import logging
import datetime
import os
from pathlib import Path
from typing import List, Optional


import discord
import pkg_resources
from discord.ext import commands
from dotenv import load_dotenv


class Client(commands.Bot):
    def __init__(
        self, *,
        log: Optional[logging.Logger] = None,
        intents: discord.Intents = discord.Intents.none()
    ):
        #* setup
        load_dotenv(dotenv_path=Path(os.path.abspath(".")+"\\.env"))

        strOwners = os.getenv("owners", None)

        #* 設定 所有者
        self.owners = [
            int(owner)for owner in strOwners.split(",")
        ] if strOwners is not None else []

        #* 需要加載的cog資料夾名
        self.__cogs_file: List[str] = ["__init__"]
        #* 開機時間
        self.start_time = datetime.datetime.utcnow()
        #* 日誌
        self.log = log or logging.getLogger()
        #* 權限意圖
        self.Intents = discord.Intents.all()

        super().__init__(
            command_prefix = "!",
            case_insensitive = True,
            owner_ids = self.owners, 
            intents = self.Intents,
            allowed_mentions = discord.AllowedMentions(
                roles = False, 
                users = True, 
                everyone = False
            )
        )

    def load(self):
        for file in self.__cogs_file:
            try:
                self.load_extension(f"cogs.commands.{file}")
            except Exception as error:
                self.log.error(f"錯誤: {error}")
            else:
                self.log.info(f"加載 cogs.commands.{file} 完成!")
        try:
            self.load_extension("cogs.events.__init__")
        except Exception as error:
            self.log.error(f"加載 cogs.events 錯誤: {error}!")
        else:
            self.log.info("加載 cogs.events 完成!")

    def run(
        self,
        token: Optional[str] = None,
        version: Optional[str] = None
    ):
        #* 執行
        self.__version__ = pkg_resources.parse_version(
            "1.0.0" if version is None else version
        )
        try:
            super().run(os.getenv("TOKEN", token), reconnect=True)
        except discord.LoginFailure:
            raise Exception("請於 https://www.discordapp.com/developers 申請Bot")

    #* event
    async def on_ready(self):
        """執行始初化/BOT開機呼叫"""
        self.load()
        print(self.user)