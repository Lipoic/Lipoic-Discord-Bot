import os
import logging
import argparse
from typing import NamedTuple, Optional
from .server import create_server

import dotenv

if __name__ == "__main__":
    from .core import LIPOIC, logging as lipoicLog

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--debug",
        help="debug mode",
        action="store_true",
    )
    parser.add_argument(
        "-l",
        "--level",
        help="logging level",
        choices=logging._nameToLevel.keys(),
        default="INFO",
        type=str,
    )
    parser.add_argument(
        "-t",
        "--token",
        help="bot token",
        type=str,
    )

    class ArgsType(NamedTuple):
        token: Optional[str]
        level: str
        debug: bool

    args: ArgsType = parser.parse_args()

    lipoicLog.init_logging(level=args.level)
    dotenv.load_dotenv()

    bot = LIPOIC(debug=args.debug)
    create_server(loop=bot.loop)
    bot.run(args.token or os.getenv("DISCORD_TOKEN"))
