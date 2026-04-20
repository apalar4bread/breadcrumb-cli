"""importer.py — Import steps from external shell history or plain text files."""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional

from breadcrumb.session import Session, add_step


class ImportError(Exception):
    """Raised when an import operation fails."""


def _strip_bash_history_number(line: str) -> str:
    """Remove leading history line numbers like '  123  command'."""
    return re.sub(r'^\s*\d+\s+', '', line)


def import_from_history_file(
    session: Session,
    path: str | Path,
    *,
    skip_blank: bool = True,
    strip_numbers: bool = True,
    limit: Optional[int] = None,
    note_prefix: Optional[str] = None,
) -> List[str]:
    """Read a shell history file and append each line as a step.

    Args:
        session:        The session to populate.
        path:           Path to the history file (e.g. ~/.bash_history).
        skip_blank:     Ignore empty / whitespace-only lines.
        strip_numbers:  Strip leading numeric indices produced by `history`.
        limit:          Maximum number of steps to import (None = all).
        note_prefix:    Optional prefix for auto-generated step notes.

    Returns:
        List of imported command strings.

    Raises:
        ImportError: If the file cannot be read.
    """
    p = Path(path)
    if not p.exists():
        raise ImportError(f"History file not found: {path}")
    if not p.is_file():
        raise ImportError(f"Path is not a file: {path}")

    try:
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        raise ImportError(f"Could not read file: {exc}") from exc

    imported: List[str] = []
    for raw in lines:
        if limit is not None and len(imported) >= limit:
            break

        line = raw.strip()
        if strip_numbers:
            line = _strip_bash_history_number(line).strip()

        if skip_blank and not line:
            continue

        note = f"{note_prefix}{line}" if note_prefix else None
        add_step(session, command=line, note=note)
        imported.append(line)

    return imported


def import_from_lines(
    session: Session,
    lines: List[str],
    *,
    skip_blank: bool = True,
    limit: Optional[int] = None,
    note_prefix: Optional[str] = None,
) -> List[str]:
    """Import steps from an in-memory list of command strings.

    Useful when the caller has already read or generated the lines.

    Args:
        session:        The session to populate.
        lines:          Command strings to import.
        skip_blank:     Ignore empty / whitespace-only lines.
        limit:          Maximum number of steps to import.
        note_prefix:    Optional prefix for auto-generated step notes.

    Returns:
        List of imported command strings.
    """
    imported: List[str] = []
    for raw in lines:
        if limit is not None and len(imported) >= limit:
            break

        line = raw.strip()
        if skip_blank and not line:
            continue

        note = f"{note_prefix}{line}" if note_prefix else None
        add_step(session, command=line, note=note)
        imported.append(line)

    return imported


def import_summary(imported: List[str]) -> str:
    """Return a human-readable summary of an import operation."""
    count = len(imported)
    if count == 0:
        return "No steps imported."
    preview = imported[:3]
    lines = [f"Imported {count} step(s):"]
    for cmd in preview:
        lines.append(f"  • {cmd}")
    if count > 3:
        lines.append(f"  … and {count - 3} more")
    return "\n".join(lines)
