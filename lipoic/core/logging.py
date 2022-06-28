import datetime
import logging
from logging import handlers
import pathlib
import re
from typing import Iterable, List, Optional, Tuple, Union

import rich
from pygments.styles.monokai import MonokaiStyle
from pygments.token import (
    Comment, Error, Keyword,
    Name, Number, Operator, String, Token
)
from rich._log_render import FormatTimeCallable, LogRender
from rich.console import ConsoleRenderable
from rich.highlighter import NullHighlighter
from rich.logging import RichHandler
from rich.syntax import ANSISyntaxTheme, PygmentsSyntaxTheme
from rich.text import Text, TextType
from rich.theme import Style, Theme

MAX_OLD_LOGS = 8

SYNTAX_THEME = {
    Token: Style(),
    Comment: Style(color="bright_black"),
    Keyword: Style(color="cyan", bold=True),
    Keyword.Constant: Style(color="bright_magenta"),
    Keyword.Namespace: Style(color="bright_red"),
    Operator: Style(bold=True),
    Operator.Word: Style(color="cyan", bold=True),
    Name.Builtin: Style(bold=True),
    Name.Builtin.Pseudo: Style(color="bright_red"),
    Name.Exception: Style(bold=True),
    Name.Class: Style(color="bright_green"),
    Name.Function: Style(color="bright_green"),
    String: Style(color="yellow"),
    Number: Style(color="cyan"),
    Error: Style(bgcolor="red"),
}


class RotatingFileHandler(handlers.RotatingFileHandler):
    def __init__(
        self,
        name: str,
        directory: Optional[pathlib.Path] = None,
        maxBytes: int = 0, backupCount: int = 0,
        encoding: str = "utf-8",
    ):
        self.baseName = name
        self.directory = directory
        log_part_re = re.compile(rf"{name}-part(?P<part>\d)\.log")
        highest_part = 0
        for file in directory.iterdir():
            match = log_part_re.match(file.name)
            if match and int(match["part"]) > highest_part:
                highest_part = int(match["part"])
        if highest_part:
            filename = directory / f"{name}-part{highest_part}.log"
        else:
            filename = directory / f"{name}.log"
        super().__init__(
            filename,
            mode="a",
            maxBytes=maxBytes,
            backupCount=backupCount,
            encoding=encoding,
            delay=False,
        )


class LipoicLogRender(LogRender):
    def __call__(
        self,
        console: "rich.Console",
        renderables: Iterable["ConsoleRenderable"],
        log_time: Optional[datetime.datetime] = None,
        time_format: Optional[Union[str, FormatTimeCallable]] = None,
        level: TextType = "",
        path: Optional[str] = None,
        line_no: Optional[int] = None,
        link_path: Optional[str] = None,
        logger_name: Optional[str] = None,
    ):
        output = Text()
        if self.show_time:
            log_time = log_time or console.get_datetime()
            log_time_display = log_time.strftime(
                time_format or self.time_format
            )
            if log_time_display == self._last_time:
                output.append(" " * (len(log_time_display) + 1))
            else:
                output.append(f"{log_time_display} ", style="log.time")
                self._last_time = log_time_display
        if self.show_level:
            output.append(level)
            output.append(" ")
        if logger_name:
            output.append(f"[{logger_name}] ", style="bright_black")

        output.append(*renderables)
        if self.show_path and path:
            path_text = Text()
            path_text.append(
                path, style=f"link file://{link_path}" if link_path else ""
            )
            if line_no:
                path_text.append(f":{line_no}")
            output.append(path_text)
        return output


class LipoicRichHandler(RichHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._log_render = LipoicLogRender(
            show_time=self._log_render.show_time,
            show_level=self._log_render.show_level,
            show_path=self._log_render.show_path,
            level_width=self._log_render.level_width,
        )


def init_logging(level: int, location: Optional[pathlib.Path] = None) -> None:
    location = location or pathlib.Path() / "logs"

    root_logger = logging.getLogger()
    base_logger = logging.getLogger("lipoic")
    dpy_logger = logging.getLogger("discord")
    warnings_logger = logging.getLogger("py.warnings")

    base_logger.setLevel(level)
    dpy_logger.setLevel(logging.WARNING)
    warnings_logger.setLevel(logging.WARNING)

    rich_console = rich.get_console()
    rich.reconfigure(tab_size=2)

    rich_console.push_theme(Theme({
        "log.time": Style(dim=True),
        "logging.level.warning": Style(color="yellow"),
        "logging.level.critical": Style(color="white", bgcolor="red"),
        "logging.level.verbose": Style(color="magenta", italic=True, dim=True),
        "logging.level.trace": Style(color="white", italic=True, dim=True),
        "repr.number": Style(color="cyan"),
        "repr.url": Style(underline=True, italic=True, bold=False, color="cyan"),
    }))

    file_formatter = logging.Formatter(
        "[{asctime}] [{levelname}] {name}: {message}", datefmt="%Y-%m-%d %H:%M:%S", style="{"
    )

    rich_formatter = logging.Formatter(
        "{message}", datefmt="[%X]", style="{"
    )
    stdout_handler = LipoicRichHandler(
        rich_tracebacks=True,
        show_path=False,
        highlighter=NullHighlighter(),
        tracebacks_theme=(
            PygmentsSyntaxTheme(MonokaiStyle)
            if rich_console.color_system == "truecolor"
            else ANSISyntaxTheme(SYNTAX_THEME)
        ),
    )
    stdout_handler.setFormatter(rich_formatter)

    root_logger.addHandler(stdout_handler)
    logging.captureWarnings(True)

    if not location.exists():
        location.mkdir(parents=True, exist_ok=True)

    previous_logs: List[pathlib.Path] = []
    latest_logs: List[Tuple[pathlib.Path, str]] = []

    for path in location.iterdir():
        match = re.match(r"latest(?P<part>-part\d+)?\.log", path.name)
        if match:
            part = match.groupdict(default="")["part"]
            latest_logs.append((path, part))
        match = re.match(r"previous(?:-part\d+)?.log", path.name)
        if match:
            previous_logs.append(path)

    for path in previous_logs:
        path.unlink()

    for path, part in latest_logs:
        path.replace(location / f"previous{part}.log")

    latest = RotatingFileHandler(
        "latest", directory=location, maxBytes=1e6, backupCount=MAX_OLD_LOGS,
    )
    all = RotatingFileHandler(
        "lipoic", directory=location, maxBytes=1e6, backupCount=MAX_OLD_LOGS,
    )

    for handler in (latest, all):
        handler.setFormatter(file_formatter)
        root_logger.addHandler(handler)
