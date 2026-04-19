"""Syntax highlighting for commands in session output."""

import re
from typing import Optional

# Patterns ordered by priority
_PATTERNS = [
    ("flag", re.compile(r"(?<= )(--?[\w-]+)")),
    ("path", re.compile(r"(?<= )(/[\w./-]+|\./[\w./-]+|~/[\w./-]*)")),
    ("string", re.compile(r'("[^"]*"|\'[^\']*\')')),
    ("number", re.compile(r"(?<= )(\d+)(?= |$)")),
    ("pipe", re.compile(r"(\||&&|;|>>|>|<)")),
]

_ANSI = {
    "flag": "\033[33m",    # yellow
    "path": "\033[36m",    # cyan
    "string": "\033[32m",  # green
    "number": "\033[35m",  # magenta
    "pipe": "\033[31m",    # red
    "cmd": "\033[1;34m",   # bold blue
    "reset": "\033[0m",
}


def highlight_command(command: str, enabled: bool = True) -> str:
    """Return a syntax-highlighted version of a shell command string."""
    if not enabled or not command:
        return command

    parts = command.split(" ", 1)
    base = _ANSI["cmd"] + parts[0] + _ANSI["reset"]
    if len(parts) == 1:
        return base

    rest = parts[1]
    rest = _apply_patterns(rest, enabled)
    return base + " " + rest


def _apply_patterns(text: str, enabled: bool) -> str:
    """Apply all highlight patterns to the non-command portion of a string."""
    # Use placeholder substitution to avoid re-matching replaced spans
    placeholders = {}
    counter = [0]

    def replace(style: str, m: re.Match) -> str:
        key = f"\x00{counter[0]}\x00"
        counter[0] += 1
        placeholders[key] = _ANSI[style] + m.group(0) + _ANSI["reset"]
        return key

    for style, pattern in _PATTERNS:
        text = pattern.sub(lambda m, s=style: replace(s, m), text)

    for key, val in placeholders.items():
        text = text.replace(key, val)

    return text


def strip_highlights(text: str) -> str:
    """Remove ANSI escape codes from a string."""
    return re.sub(r"\033\[[0-9;]*m", "", text)
