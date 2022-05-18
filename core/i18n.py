import json
import os
import pathlib
from typing import Literal, Union

import discord

localesType = Literal["en-US", "zh-CN", "zh-TW"]
defaultLocale = "zh-TW"
locales = {
    "en-us": {"nativeName": "English, US", "languageName": "English, US"},
    "zh-cn": {"nativeName": "中文", "languageName": "Chinese, China"},
    "zh-tw": {"nativeName": "繁體中文", "languageName": "Chinese, Taiwan"},
}


class Translator:
    def __init__(self, name: str, file_location: Union[str, pathlib.Path, os.PathLike]):
        self.cog_folder = pathlib.Path(file_location).resolve().parent
        self.cog_name = name
        self.translations = {}

        # self.load_translations()

    def getLocales():
        return [locale for locale in locales.keys()]

    def getLocale(locale: localesType):
        with open(f"locales/{locale}.json", encoding="utf-8") as file:
            return json.load(file)

    # def load_translations
