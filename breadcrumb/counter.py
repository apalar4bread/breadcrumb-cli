"""counter.py — count steps matching various criteria in a session."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from breadcrumb.session import Session


class CounterError(Exception):
    pass


@dataclass
class CountResult:
    total: int
    matched: int
    criteria: str

    @property
    def summary(self) -> str:
        return f"{self.matched}/{self.total} steps matched '{self.criteria}'"


def count_by_command(session: Session, pattern: str, case_sensitive: bool = False) -> CountResult:
    """Count steps whose command contains *pattern*."""
    if not pattern:
        raise CounterError("pattern must not be empty")
    needle = pattern if case_sensitive else pattern.lower()
    matched = 0
    for step in session.steps:
        haystack = step.command if case_sensitive else step.command.lower()
        if needle in haystack:
            matched += 1
    return CountResult(total=len(session.steps), matched=matched, criteria=pattern)


def count_by_note(session: Session, pattern: str, case_sensitive: bool = False) -> CountResult:
    """Count steps whose note contains *pattern*."""
    if not pattern:
        raise CounterError("pattern must not be empty")
    needle = pattern if case_sensitive else pattern.lower()
    matched = 0
    for step in session.steps:
        note = step.note or ""
        haystack = note if case_sensitive else note.lower()
        if needle in haystack:
            matched += 1
    return CountResult(total=len(session.steps), matched=matched, criteria=pattern)


def count_by_metadata_key(session: Session, key: str) -> CountResult:
    """Count steps that have a given metadata key set (truthy value)."""
    if not key:
        raise CounterError("key must not be empty")
    matched = sum(1 for step in session.steps if step.metadata.get(key))
    return CountResult(total=len(session.steps), matched=matched, criteria=key)


def count_all(session: Session) -> int:
    """Return total number of steps in the session."""
    return len(session.steps)
