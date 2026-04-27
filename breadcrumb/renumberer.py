"""Renumberer: reassign sequential step numbers/positions stored in metadata."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from breadcrumb.session import Session, Step


class RenumberError(Exception):
    pass


@dataclass
class RenumberResult:
    session: Session
    original_count: int
    renumbered_count: int

    @property
    def summary(self) -> str:
        return (
            f"Renumbered {self.renumbered_count} of {self.original_count} "
            f"steps in '{self.session.name}'."
        )


def renumber_steps(
    session: Session,
    start: int = 1,
    step: int = 1,
    key: str = "step_number",
) -> RenumberResult:
    """Assign sequential numbers to each step, stored under *key* in metadata.

    Args:
        session: The session whose steps will be renumbered.
        start:   The first number to assign (default 1).
        step:    Increment between numbers (default 1).
        key:     Metadata key to write the number into (default 'step_number').

    Returns:
        A RenumberResult with the mutated session and counts.

    Raises:
        RenumberError: If *start* or *step* are not positive integers.
    """
    if start < 1:
        raise RenumberError(f"start must be >= 1, got {start}")
    if step < 1:
        raise RenumberError(f"step must be >= 1, got {step}")
    if not key or not key.strip():
        raise RenumberError("key must be a non-empty string")

    key = key.strip()
    original_count = len(session.steps)
    current = start
    for s in session.steps:
        s.metadata[key] = current
        current += step

    return RenumberResult(
        session=session,
        original_count=original_count,
        renumbered_count=original_count,
    )


def clear_numbers(session: Session, key: str = "step_number") -> int:
    """Remove the *key* metadata entry from all steps.

    Returns the number of steps that had the key removed.
    """
    if not key or not key.strip():
        raise RenumberError("key must be a non-empty string")
    key = key.strip()
    removed = 0
    for s in session.steps:
        if key in s.metadata:
            del s.metadata[key]
            removed += 1
    return removed


def get_number(step: Step, key: str = "step_number"):
    """Return the stored number for a step, or None if not set."""
    return step.metadata.get(key)
