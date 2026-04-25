"""Deduplicator: collapse consecutive identical commands into a single step."""

from dataclasses import dataclass, field
from typing import List

from breadcrumb.session import Session, Step


class DeduplicatorError(Exception):
    pass


@dataclass
class DeduplicateResult:
    original_count: int
    final_count: int
    removed_count: int
    session: Session

    @property
    def summary(self) -> str:
        return (
            f"Removed {self.removed_count} consecutive duplicate(s): "
            f"{self.original_count} → {self.final_count} steps."
        )


def deduplicate_consecutive(session: Session) -> DeduplicateResult:
    """Remove consecutive steps with identical commands (case-insensitive).

    The first occurrence in each run is kept; subsequent identical neighbours
    are dropped.  Non-consecutive duplicates are left untouched.
    """
    if not session.steps:
        return DeduplicateResult(
            original_count=0,
            final_count=0,
            removed_count=0,
            session=session,
        )

    kept: List[Step] = [session.steps[0]]
    for step in session.steps[1:]:
        if step.command.strip().lower() != kept[-1].command.strip().lower():
            kept.append(step)

    removed = len(session.steps) - len(kept)
    session.steps = kept
    return DeduplicateResult(
        original_count=len(kept) + removed,
        final_count=len(kept),
        removed_count=removed,
        session=session,
    )


def deduplicate_all(session: Session) -> DeduplicateResult:
    """Remove every duplicate command, keeping only the first occurrence.

    Unlike ``deduplicate_consecutive`` this scans the entire step list so
    a command that reappears later is also removed.
    """
    if not session.steps:
        return DeduplicateResult(
            original_count=0,
            final_count=0,
            removed_count=0,
            session=session,
        )

    seen: set = set()
    kept: List[Step] = []
    for step in session.steps:
        key = step.command.strip().lower()
        if key not in seen:
            seen.add(key)
            kept.append(step)

    removed = len(session.steps) - len(kept)
    session.steps = kept
    return DeduplicateResult(
        original_count=len(kept) + removed,
        final_count=len(kept),
        removed_count=removed,
        session=session,
    )
