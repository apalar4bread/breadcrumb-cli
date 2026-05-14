"""Timestamper: apply or update human-readable time labels on steps."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from breadcrumb.session import Session


class TimestamperError(Exception):
    pass


@dataclass
class TimestampResult:
    session_id: str
    updated_indices: List[int] = field(default_factory=list)
    skipped_indices: List[int] = field(default_factory=list)

    @property
    def updated_count(self) -> int:
        return len(self.updated_indices)

    def summary(self) -> str:
        return (
            f"Updated {self.updated_count} step(s), "
            f"skipped {len(self.skipped_indices)}."
        )


META_KEY = "time_label"
FMT = "%Y-%m-%d %H:%M:%S"


def apply_time_labels(
    session: Session,
    overwrite: bool = False,
    fmt: str = FMT,
) -> TimestampResult:
    """Stamp every step with a human-readable time_label derived from its timestamp.

    Steps that already have a time_label are skipped unless *overwrite* is True.
    """
    if not session.steps:
        raise TimestamperError("Session has no steps to timestamp.")

    result = TimestampResult(session_id=session.id)

    for idx, step in enumerate(session.steps):
        if META_KEY in step.metadata and not overwrite:
            result.skipped_indices.append(idx)
            continue
        try:
            dt = datetime.fromisoformat(step.timestamp)
            label = dt.strftime(fmt)
        except (ValueError, AttributeError):
            result.skipped_indices.append(idx)
            continue
        step.metadata[META_KEY] = label
        result.updated_indices.append(idx)

    return result


def clear_time_labels(session: Session) -> int:
    """Remove time_label metadata from all steps. Returns number of labels removed."""
    removed = 0
    for step in session.steps:
        if META_KEY in step.metadata:
            del step.metadata[META_KEY]
            removed += 1
    return removed


def get_time_label(session: Session, index: int) -> Optional[str]:
    """Return the time_label for a step, or None if not set."""
    if index < 0 or index >= len(session.steps):
        raise TimestamperError(f"Step index {index} out of range.")
    return session.steps[index].metadata.get(META_KEY)
