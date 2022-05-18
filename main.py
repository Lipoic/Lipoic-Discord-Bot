__version__ = "0.0.1"

if __name__ == "__main__":
    from core import LIPOIC, logging
    import dotenv
    import os

    logging.init_logging(level="INFO")

    dotenv.load_dotenv()

    bot = LIPOIC()
    bot.run(os.getenv("DISCORD_TOKEN"))
