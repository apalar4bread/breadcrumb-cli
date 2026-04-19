"""Pause and resume sessions by marking them inactive/active."""

from dataclasses import dataclass
from typing import Optional


class PauseError(Exception):
    pass


_PAUSED_KEY = "paused"


def pause_session(session) -> None:
    """Mark a session as paused."""
    if is_paused(session):
        raise PauseError(f"Session '{session.name}' is already paused.")
    session.metadata[_PAUSED_KEY] = True


def resume_session(session) -> None:
    """Resume a paused session."""
    if not is_paused(session):
        raise PauseError(f"Session '{session.name}' is not paused.")
    session.metadata.pop(_PAUSED_KEY, None)


def is_paused(session) -> bool:
    """Return True if the session is currently paused."""
    return bool(session.metadata.get(_PAUSED_KEY, False))


def list_paused(sessions: list) -> list:
    """Return all sessions that are currently paused."""
    return [s for s in sessions if is_paused(s)]


def format_pause_status(session) -> str:
    """Return a human-readable pause status string for a session."""
    status = "paused" if is_paused(session) else "active"
    return f"[{session.name}] status: {status}"
