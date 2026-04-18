"""Trim steps from sessions by index range or count."""

from typing import Optional
from breadcrumb.session import Session


class TrimError(ValueError):
    pass


def trim_steps(
    session: Session,
    start: Optional[int] = None,
    end: Optional[int] = None,
) -> Session:
    """Return a new session keeping only steps in [start, end) (0-indexed)."""
    steps = session.steps
    n = len(steps)

    if n == 0:
        raise TrimError("Session has no steps to trim.")

    start = start if start is not None else 0
    end = end if end is not None else n

    if start < 0 or end < 0:
        raise TrimError("start and end must be non-negative.")
    if start >= end:
        raise TrimError(f"start ({start}) must be less than end ({end}).")
    if start >= n:
        raise TrimError(f"start ({start}) is out of range for session with {n} steps.")

    end = min(end, n)

    trimmed = Session(
        id=session.id,
        name=session.name,
        created_at=session.created_at,
        tags=list(session.tags),
        steps=steps[start:end],
    )
    return trimmed


def trim_last(session: Session, keep: int) -> Session:
    """Keep only the last `keep` steps."""
    if keep <= 0:
        raise TrimError("keep must be a positive integer.")
    n = len(session.steps)
    start = max(0, n - keep)
    return trim_steps(session, start=start, end=n)


def trim_first(session: Session, keep: int) -> Session:
    """Keep only the first `keep` steps."""
    if keep <= 0:
        raise TrimError("keep must be a positive integer.")
    return trim_steps(session, start=0, end=keep)
