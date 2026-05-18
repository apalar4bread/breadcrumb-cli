"""Namer module: suggest and auto-generate session names from step content."""

from __future__ import annotations

from typing import List, Optional

from breadcrumb.session import Session


class NamerError(Exception):
    pass


def _top_words(commands: List[str], n: int = 3) -> List[str]:
    """Return the n most frequent meaningful words from a list of commands."""
    stopwords = {"sudo", "the", "a", "an", "and", "or", "in", "to", "of", "-v", "--help"}
    freq: dict[str, int] = {}
    for cmd in commands:
        for token in cmd.lower().split():
            token = token.strip("-")
            if token and token not in stopwords and len(token) > 1:
                freq[token] = freq.get(token, 0) + 1
    ranked = sorted(freq.items(), key=lambda x: -x[1])
    return [w for w, _ in ranked[:n]]


def suggest_name(session: Session, max_words: int = 3) -> str:
    """Suggest a session name based on the most common command words."""
    if not session.steps:
        raise NamerError("Cannot suggest a name for a session with no steps.")
    commands = [s.command for s in session.steps if s.command.strip()]
    if not commands:
        raise NamerError("No non-empty commands found in session.")
    words = _top_words(commands, n=max_words)
    if not words:
        raise NamerError("Could not derive meaningful words from commands.")
    return "-".join(words)


def auto_name(session: Session, prefix: str = "session", max_words: int = 3) -> str:
    """Return a name suggestion, falling back to a prefix+step-count name."""
    try:
        return suggest_name(session, max_words=max_words)
    except NamerError:
        return f"{prefix}-{len(session.steps)}-steps"


def apply_suggested_name(session: Session, override: bool = False) -> str:
    """Apply a suggested name to the session if it has no meaningful name yet.

    Returns the name that was applied (or already present).
    """
    placeholder_patterns = ["untitled", "new session", "session"]
    current = session.name.strip().lower()
    is_placeholder = any(current.startswith(p) for p in placeholder_patterns)
    if not is_placeholder and not override:
        return session.name
    new_name = auto_name(session)
    session.name = new_name
    return new_name
