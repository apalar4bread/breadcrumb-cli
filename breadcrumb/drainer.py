"""drainer.py — drain (consume) steps from a session one at a time, tracking position."""

from dataclasses import dataclass, field
from typing import Optional
from breadcrumb.session import Session, Step


class DrainError(Exception):
    pass


@dataclass
class DrainResult:
    step: Step
    index: int
    remaining: int

    def summary(self) -> str:
        return f"Drained step {self.index + 1} — {self.remaining} step(s) remaining."


def drain_next(session: Session) -> DrainResult:
    """Remove and return the first step from the session."""
    if not session.steps:
        raise DrainError(f"Session '{session.name}' has no steps to drain.")

    step = session.steps.pop(0)
    return DrainResult(step=step, index=0, remaining=len(session.steps))


def drain_last(session: Session) -> DrainResult:
    """Remove and return the last step from the session."""
    if not session.steps:
        raise DrainError(f"Session '{session.name}' has no steps to drain.")

    index = len(session.steps) - 1
    step = session.steps.pop(index)
    return DrainResult(step=step, index=index, remaining=len(session.steps))


def drain_at(session: Session, index: int) -> DrainResult:
    """Remove and return the step at the given index."""
    if not session.steps:
        raise DrainError(f"Session '{session.name}' has no steps to drain.")
    if index < 0 or index >= len(session.steps):
        raise DrainError(
            f"Index {index} out of range for session '{session.name}' "
            f"with {len(session.steps)} step(s)."
        )

    step = session.steps.pop(index)
    return DrainResult(step=step, index=index, remaining=len(session.steps))


def drain_all(session: Session) -> list[DrainResult]:
    """Drain every step from the session, returning results in order."""
    if not session.steps:
        raise DrainError(f"Session '{session.name}' has no steps to drain.")

    results = []
    original_count = len(session.steps)
    for i in range(original_count):
        step = session.steps.pop(0)
        results.append(DrainResult(step=step, index=i, remaining=original_count - i - 1))
    return results
