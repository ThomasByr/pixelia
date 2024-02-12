import logging
import os
import sys

from .fmt import UsefulFormatter, UselessHandler

__all__ = ["init_logger"]

try:
    import colorama  # type: ignore

    colorama.init()
except (ImportError, OSError):
    HAS_COLORAMA = False
else:
    HAS_COLORAMA = True


def supports_color():
    """
    Return True if the running system's terminal supports color,
    and False otherwise.\\
    thanks to https://github.com/django/django/blob/main/django/core/management/color.py
    """

    def vt_codes_enabled_in_windows_registry():
        """
        Check the Windows Registry to see if VT code handling has been enabled
        by default, see https://superuser.com/a/1300251/447564.
        """
        try:
            # winreg is only available on Windows.
            import winreg
        except ImportError:
            return False
        try:
            reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Console")
            reg_key_value, _ = winreg.QueryValueEx(reg_key, "VirtualTerminalLevel")
        except FileNotFoundError:
            return False
        return reg_key_value == 1

    # isatty is not always implemented, #6223.
    is_a_tty = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

    return is_a_tty and (
        sys.platform != "win32"
        or HAS_COLORAMA
        or "ANSICON" in os.environ
        or
        # Windows Terminal supports VT codes.
        "WT_SESSION" in os.environ
        or
        # Microsoft Visual Studio Code's built-in terminal supports colors.
        os.environ.get("TERM_PROGRAM") == "vscode"
        or vt_codes_enabled_in_windows_registry()
    )


def init_logger(log_lvl: int = logging.INFO) -> bool:
    """
    Initializes the logger for the application\\
    This sets the global configuration for the logger

    ## Parameters
    - `log_lvl` - int, (optional)
    the logging level (see `logging` module for more info)
    defaults to `logging.INFO`

    ## Returns
    - bool - if color is supported for the console
    """
    colored_output = supports_color()

    # create console handler with a higher log level
    console_handler = UselessHandler()
    console_handler.setLevel(logging.DEBUG)  # lowest level to log
    console_handler.setFormatter(UsefulFormatter(colored_output=colored_output))

    # create file handler which logs even debug messages
    file_handler = logging.FileHandler(".log", mode="w", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)  # lowest level to log
    file_handler.setFormatter(UsefulFormatter(colored_output=False))

    logging.basicConfig(
        level=log_lvl,
        style="%",
        handlers=[console_handler, file_handler],
    )
    return colored_output
