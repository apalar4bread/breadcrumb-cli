"""Search sessions and steps by keyword or metadata."""

from typing import List, Tuple
from breadcrumb.session import Session, Step


def search_steps_by_command(
    sessions: List[Session], keyword: str, case_sensitive: bool = False
) -> List[Tuple[Session, Step]]:
    """Return (session, step) pairs where the command contains keyword."""
    results = []
    needle = keyword if case_sensitive else keyword.lower()
    for session in sessions:
        for step in session.steps:
            haystack = step.command if case_sensitive else step.command.lower()
            if needle in haystack:
                results.append((session, step))
    return results


def search_steps_by_note(
    sessions: List[Session], keyword: str, case_sensitive: bool = False
) -> List[Tuple[Session, Step]]:
    """Return (session, step) pairs where the note contains keyword."""
    results = []
    needle = keyword if case_sensitive else keyword.lower()
    for session in sessions:
        for step in session.steps:
            note = step.metadata.get("note", "")
            haystack = note if case_sensitive else note.lower()
            if needle in haystack:
                results.append((session, step))
    return results


def search_sessions_by_name(
    sessions: List[Session], keyword: str, case_sensitive: bool = False
) -> List[Session]:
    """Return sessions whose name contains keyword."""
    needle = keyword if case_sensitive else keyword.lower()
    return [
        s for s in sessions
        if needle in (s.name if case_sensitive else s.name.lower())
    ]
