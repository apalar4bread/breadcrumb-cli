"""Colorize formatted output for terminal display."""

from dataclasses import dataclass
from typing import Optional

ANSI = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "cyan": "\033[36m",
    "white": "\033[37m",
}


def colorize(text: str, *styles: str,n    """Wrap ANSI codes. No-op if enabled=False."""
    if not enabled:
        return text
    codes = "".join(ANSI[s] for s in styles if s in ANSI)
    return f"{codes}{text}{ANSI['reset']}"


def color_command(cmd: str, enabled: bool = True) -> str:
    return colorize(cmd, "green", "bold", enabled=enabled)


def color_note(note: str, enabled: bool = True) -> str:
    return colorize(note, "cyan", enabled=enabled)


def color_tag(tag: str, enabled: bool = True) -> str:
    return colorize(f"#{tag}", "yellow", enabled=enabled)


def color_label(label: str, enabled: bool = True) -> str:
    return colorize(f"[{label}]", "blue", "bold", enabled=enabled)


def color_index(idx: int, enabled: bool = True) -> str:
    return colorize(str(idx), "dim", enabled=enabled)


def color_error(msg: str, enabled: bool = True) -> str:
    return colorize(msg, "red", "bold", enabled=enabled)


def color_success(msg: str, enabled: bool = True) -> str:
    return colorize(msg, "green", enabled=enabled)


def color_session_name(name: str, enabled: bool = True) -> str:
    return colorize(name, "white", "bold", enabled=enabled)
