"""cursor.py — track and move a named cursor position within a session's steps."""

from __future__ import annotations
from dataclasses import dataclass
from breadcrumb.session import Session

_CURSOR_KEY = "cursor_position"


class CursorError(Exception):
    pass


@dataclass
class CursorResult:
    session_name: str
    position: int
    command: str
    total_steps: int

    def __str__(self) -> str:
        return (
            f"[{self.session_name}] cursor at step {self.position + 1}/{self.total_steps}: "
            f"{self.command}"
        )


def set_cursor(session: Session, index: int) -> CursorResult:
    """Move the cursor to the given step index (0-based)."""
    if not session.steps:
        raise CursorError("Cannot set cursor on a session with no steps.")
    if index < 0 or index >= len(session.steps):
        raise CursorError(
            f"Index {index} out of range for session with {len(session.steps)} steps."
        )
    session.metadata[_CURSOR_KEY] = index
    step = session.steps[index]
    return CursorResult(
        session_name=session.name,
        position=index,
        command=step.command,
        total_steps=len(session.steps),
    )


def get_cursor(session: Session) -> CursorResult:
    """Return the current cursor position, defaulting to 0."""
    if not session.steps:
        raise CursorError("Session has no steps.")
    index = int(session.metadata.get(_CURSOR_KEY, 0))
    index = max(0, min(index, len(session.steps) - 1))
    step = session.steps[index]
    return CursorResult(
        session_name=session.name,
        position=index,
        command=step.command,
        total_steps=len(session.steps),
    )


def advance_cursor(session: Session, by: int = 1) -> CursorResult:
    """Move the cursor forward by *by* steps, clamping at the last step."""
    if not session.steps:
        raise CursorError("Session has no steps.")
    current = int(session.metadata.get(_CURSOR_KEY, 0))
    new_index = min(current + by, len(session.steps) - 1)
    return set_cursor(session, new_index)


def reset_cursor(session: Session) -> None:
    """Remove the cursor position from session metadata."""
    session.metadata.pop(_CURSOR_KEY, None)


def is_at_end(session: Session) -> bool:
    """Return True if the cursor is at the last step."""
    if not session.steps:
        return False
    index = int(session.metadata.get(_CURSOR_KEY, 0))
    return index >= len(session.steps) - 1
