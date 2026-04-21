"""Zipper: interleave steps from two sessions into a single merged session."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from breadcrumb.session import Session, Step


class ZipError(Exception):
    pass


@dataclass
class ZipResult:
    session: Session
    total_steps: int
    left_count: int
    right_count: int


def zip_sessions(
    left: Session,
    right: Session,
    name: Optional[str] = None,
    strict: bool = False,
) -> ZipResult:
    """Interleave steps from *left* and *right* alternately (left-first).

    If *strict* is True both sessions must have the same number of steps.
    """
    if strict and len(left.steps) != len(right.steps):
        raise ZipError(
            f"strict mode: step counts differ ({len(left.steps)} vs {len(right.steps)})"
        )

    session_name = name or f"{left.name} + {right.name}"
    result = Session(name=session_name)
    result.tags = sorted(set(left.tags) | set(right.tags))

    pairs = zip(left.steps, right.steps)
    for l_step, r_step in pairs:
        result.steps.append(_copy_step(l_step))
        result.steps.append(_copy_step(r_step))

    # append any remaining steps from the longer session
    longer = left.steps if len(left.steps) > len(right.steps) else right.steps
    shorter_len = min(len(left.steps), len(right.steps))
    for step in longer[shorter_len:]:
        result.steps.append(_copy_step(step))

    return ZipResult(
        session=result,
        total_steps=len(result.steps),
        left_count=len(left.steps),
        right_count=len(right.steps),
    )


def format_zip_result(result: ZipResult) -> str:
    lines = [
        f"Zipped session : {result.session.name}",
        f"Total steps    : {result.total_steps}",
        f"From left      : {result.left_count}",
        f"From right     : {result.right_count}",
    ]
    return "\n".join(lines)


def _copy_step(step: Step) -> Step:
    return Step(
        command=step.command,
        note=step.note,
        timestamp=step.timestamp,
        metadata=dict(step.metadata),
    )
