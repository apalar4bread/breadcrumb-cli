"""Filter session steps by various criteria."""
from typing import List, Optional
from breadcrumb.session import Session, Step
from datetime import datetime


class FilterError(ValueError):
    pass


def filter_by_command(session: Session, pattern: str, case_sensitive: bool = False) -> List[Step]:
    """Return steps whose command contains the pattern."""
    if not pattern.strip():
        raise FilterError("Pattern must not be empty.")
    needle = pattern if case_sensitive else pattern.lower()
    return [
        s for s in session.steps
        if needle in (s.command if case_sensitive else s.command.lower())
    ]


def filter_by_note(session: Session, pattern: str, case_sensitive: bool = False) -> List[Step]:
    """Return steps whose note contains the pattern."""
    if not pattern.strip():
        raise FilterError("Pattern must not be empty.")
    needle = pattern if case_sensitive else pattern.lower()
    return [
        s for s in session.steps
        if s.note and needle in (s.note if case_sensitive else s.note.lower())
    ]


def filter_by_metadata_key(session: Session, key: str) -> List[Step]:
    """Return steps that have a specific metadata key set."""
    if not key.strip():
        raise FilterError("Metadata key must not be empty.")
    return [s for s in session.steps if key in s.metadata]


def filter_by_date_range(
    session: Session,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> List[Step]:
    """Return steps whose timestamp falls within [start, end]."""
    results = []
    for step in session.steps:
        ts = datetime.fromisoformat(step.timestamp)
        if start and ts < start:
            continue
        if end and ts > end:
            continue
        results.append(step)
    return results
