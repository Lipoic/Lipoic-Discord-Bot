
import os
import dotenv

if __name__ == "__main__":
    from .core import LIPOIC, logging
    logging.init_logging(level="INFO")

    dotenv.load_dotenv()

    bot = LIPOIC()
    bot.run(os.getenv("DISCORD_TOKEN"))
