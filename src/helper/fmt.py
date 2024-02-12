import logging
import os
import re
import signal
import sys
from typing import Any

from termcolor import colored
from typing_extensions import override

__all__ = ["UsefulFormatter", "UselessHandler"]

emoji_pattern = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "\U00002500-\U00002BEF"  # chinese char
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "\U0001f926-\U0001f937"
    "\U00010000-\U0010ffff"
    "\u2640-\u2642"
    "\u2600-\u2B55"
    "\u200d"
    "\u23cf"
    "\u23e9"
    "\u231a"
    "\ufe0f"  # dingbats
    "\u3030"
    "]+",
    re.UNICODE,
)


# hide and show cursor functions from colorama
# someone stripped colorama to only keep these functions
# https://stackoverflow.com/a/10455937/13708995

if os.name == "nt":
    import msvcrt  # type: ignore # noqa
    import ctypes  # type: ignore # noqa

    class __CursorInfo(ctypes.Structure):
        _fields_ = [("size", ctypes.c_int), ("visible", ctypes.c_byte)]


def hide_cursor():
    if os.name == "nt":
        ci = __CursorInfo()
        handle = ctypes.windll.kernel32.GetStdHandle(-11)
        ctypes.windll.kernel32.GetConsoleCursorInfo(handle, ctypes.byref(ci))
        ci.visible = False
        ctypes.windll.kernel32.SetConsoleCursorInfo(handle, ctypes.byref(ci))
    elif os.name == "posix":
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()


def show_cursor():
    if os.name == "nt":
        ci = __CursorInfo()
        handle = ctypes.windll.kernel32.GetStdHandle(-11)
        ctypes.windll.kernel32.GetConsoleCursorInfo(handle, ctypes.byref(ci))
        ci.visible = True
        ctypes.windll.kernel32.SetConsoleCursorInfo(handle, ctypes.byref(ci))
    elif os.name == "posix":
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()


def formatter(
    c: str,
    colored_output: bool = True,
    name_width: int = 10,
    attrs: list[str] = None,
) -> str:
    if colored_output:
        return (
            f"{colored('%(asctime)s', 'grey', attrs=['bold'])} {colored('%(levelname)8s', c, attrs=attrs)}"
            f"{colored(f'%(name){name_width}s', 'magenta')} %(message)s"
        )
    return f"%(asctime)s %(levelname)8s %(name){name_width}s %(message)s"


class UsefulFormatter(logging.Formatter):
    name_width = 10
    dt_fmt = "%Y-%m-%d %H:%M:%S"

    def __init__(self, *args: Any, colored_output: bool = True, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.colored_output = colored_output

    @override
    def format(self, record: logging.LogRecord) -> str:
        self.name_width = max(len(record.name) + 1, self.name_width)
        formats = {
            logging.DEBUG: formatter("green", self.colored_output, self.name_width),
            logging.INFO: formatter("blue", self.colored_output, self.name_width),
            logging.WARNING: formatter("yellow", self.colored_output, self.name_width),
            logging.ERROR: formatter("red", self.colored_output, self.name_width),
            logging.CRITICAL: formatter("red", self.colored_output, self.name_width, ["bold"]),
        }
        log_fmt = formats.get(record.levelno)
        fmt = logging.Formatter(log_fmt, self.dt_fmt, style="%")
        if not self.colored_output:
            record.msg = emoji_pattern.sub("", record.msg)
        return fmt.format(record)


class UselessHandler(logging.StreamHandler):
    @override
    def emit(self, record: logging.LogRecord) -> None:
        super().emit(record)
        if record.levelno >= logging.CRITICAL:  # exit on critical errors
            show_cursor()
            print("Terminated")
            os.kill(os.getpid(), signal.SIGTERM)
