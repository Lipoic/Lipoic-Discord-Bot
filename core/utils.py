import json
from typing import Literal

localesType = Literal["en-US", "zh-CN", "zh-TW"]
defaultLocale = "zh-TW"
locales = {
    "en-US": {"nativeName": "English, US", "languageName": "English, US"},
    "zh-CN": {"nativeName": "中文", "languageName": "Chinese, China"},
    "zh-TW": {"nativeName": "繁體中文", "languageName": "Chinese, Taiwan"},
}


class Translator:
    def __init__(self):
        ...

    def getLocales():
        return [locale for locale in locales.keys()]

    def getLocale(locale: localesType):
        with open(f"locales/{locale}.json", encoding="utf-8") as file:
            return json.load(file)
