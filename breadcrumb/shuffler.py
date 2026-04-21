"""Shuffler: randomly reorder steps in a session."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Optional

from breadcrumb.session import Session, Step


class ShuffleError(Exception):
    pass


@dataclass
class ShuffleResult:
    session_id: str
    session_name: str
    original_order: list[str]  # commands before shuffle
    new_order: list[str]       # commands after shuffle
    step_count: int


def shuffle_steps(session: Session, seed: Optional[int] = None) -> ShuffleResult:
    """Randomly reorder all steps in the session in-place.

    Args:
        session: The session whose steps will be shuffled.
        seed: Optional random seed for reproducibility.

    Returns:
        A ShuffleResult describing what changed.

    Raises:
        ShuffleError: If the session has fewer than 2 steps.
    """
    if len(session.steps) < 2:
        raise ShuffleError(
            f"Session '{session.name}' needs at least 2 steps to shuffle "
            f"(has {len(session.steps)})."
        )

    original_order = [step.command for step in session.steps]

    rng = random.Random(seed)
    rng.shuffle(session.steps)

    new_order = [step.command for step in session.steps]

    return ShuffleResult(
        session_id=session.id,
        session_name=session.name,
        original_order=original_order,
        new_order=new_order,
        step_count=len(session.steps),
    )


def format_shuffle_result(result: ShuffleResult) -> str:
    """Return a human-readable summary of a shuffle operation."""
    lines = [
        f"Shuffled {result.step_count} steps in '{result.session_name}':",
    ]
    width = len(str(result.step_count))
    for i, (before, after) in enumerate(
        zip(result.original_order, result.new_order), start=1
    ):
        marker = "  " if before == after else "* "
        lines.append(f"  {marker}{i:{width}}. {after}")
    return "\n".join(lines)
