from logging.config import fileConfig
from core import Client

fileConfig("logging_config.ini")


if __name__ == "__main__":
    bot = Client()
    bot.run()
