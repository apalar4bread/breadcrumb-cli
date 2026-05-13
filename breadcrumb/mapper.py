"""mapper.py — build a command-to-steps mapping across one or more sessions."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from breadcrumb.session import Session, Step


class MapperError(Exception):
    pass


@dataclass
class MapEntry:
    command: str
    occurrences: List[Tuple[str, int]] = field(default_factory=list)  # (session_name, step_index)

    @property
    def count(self) -> int:
        return len(self.occurrences)


@dataclass
class CommandMap:
    entries: Dict[str, MapEntry] = field(default_factory=dict)

    @property
    def total_commands(self) -> int:
        return len(self.entries)

    @property
    def total_occurrences(self) -> int:
        return sum(e.count for e in self.entries.values())


def build_map(sessions: List[Session], *, case_sensitive: bool = False) -> CommandMap:
    """Build a CommandMap from a list of sessions."""
    if not sessions:
        raise MapperError("At least one session is required to build a map.")

    cmap = CommandMap()
    for session in sessions:
        for idx, step in enumerate(session.steps):
            cmd = step.command if case_sensitive else step.command.lower()
            cmd = cmd.strip()
            if not cmd:
                continue
            if cmd not in cmap.entries:
                cmap.entries[cmd] = MapEntry(command=cmd)
            cmap.entries[cmd].occurrences.append((session.name, idx))
    return cmap


def top_commands(cmap: CommandMap, n: int = 5) -> List[MapEntry]:
    """Return the top-n most frequent commands."""
    sorted_entries = sorted(cmap.entries.values(), key=lambda e: e.count, reverse=True)
    return sorted_entries[:n]


def format_map(cmap: CommandMap, limit: int = 10) -> str:
    """Return a human-readable summary of the command map."""
    if not cmap.entries:
        return "No commands found."
    lines = [f"Command map ({cmap.total_commands} unique, {cmap.total_occurrences} total):"]
    for entry in top_commands(cmap, n=limit):
        lines.append(f"  {entry.command!r:40s}  x{entry.count}")
    return "\n".join(lines)
