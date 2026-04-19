"""Revert a session to a previous snapshot or step count."""

from dataclasses import dataclass
from typing import Optional
from breadcrumb.session import Session


class RevertError(Exception):
    pass


@dataclass
class RevertResult:
    original_step_count: int
    reverted_step_count: int
    session_name: str


def revert_to_step(session: Session, step_index: int) -> RevertResult:
    """Revert session to contain only steps up to and including step_index (0-based)."""
    if not session.steps:
        raise RevertError("Session has no steps to revert.")

    total = len(session.steps)
    if step_index < 0:
        raise RevertError(f"step_index must be >= 0, got {step_index}.")
    if step_index >= total:
        raise RevertError(
            f"step_index {step_index} out of range for session with {total} steps."
        )

    original_count = total
    session.steps = session.steps[: step_index + 1]
    return RevertResult(
        original_step_count=original_count,
        reverted_step_count=len(session.steps),
        session_name=session.name,
    )


def revert_last_n(session: Session, n: int) -> RevertResult:
    """Remove the last n steps from a session."""
    if n <= 0:
        raise RevertError(f"n must be a positive integer, got {n}.")
    if not session.steps:
        raise RevertError("Session has no steps to revert.")
    if n > len(session.steps):
        raise RevertError(
            f"Cannot remove {n} steps from a session with only {len(session.steps)} steps."
        )

    original_count = len(session.steps)
    session.steps = session.steps[:-n]
    return RevertResult(
        original_step_count=original_count,
        reverted_step_count=len(session.steps),
        session_name=session.name,
    )


def format_revert_result(result: RevertResult) -> str:
    removed = result.original_step_count - result.reverted_step_count
    return (
        f"Session '{result.session_name}' reverted: "
        f"{result.original_step_count} -> {result.reverted_step_count} steps "
        f"({removed} removed)."
    )
