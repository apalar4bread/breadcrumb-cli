"""Session step rotator — shift steps left or right within a session."""

from dataclasses import dataclass
from typing import List
from breadcrumb.session import Session, Step


class RotateError(Exception):
    pass


@dataclass
class RotateResult:
    session_name: str
    direction: str
    positions: int
    step_count: int


def rotate_steps(session: Session, positions: int = 1, direction: str = "left") -> RotateResult:
    """Rotate all steps in the session left or right by `positions`."""
    if direction not in ("left", "right"):
        raise RotateError(f"Invalid direction '{direction}'. Use 'left' or 'right'.")
    if positions < 1:
        raise RotateError(f"Positions must be >= 1, got {positions}.")

    steps = session.steps
    if not steps:
        raise RotateError("Cannot rotate an empty session.")

    n = len(steps)
    effective = positions % n
    if effective == 0:
        return RotateResult(
            session_name=session.name,
            direction=direction,
            positions=positions,
            step_count=n,
        )

    if direction == "left":
        rotated = steps[effective:] + steps[:effective]
    else:
        rotated = steps[n - effective:] + steps[: n - effective]

    session.steps = rotated
    return RotateResult(
        session_name=session.name,
        direction=direction,
        positions=positions,
        step_count=n,
    )


def format_rotate_result(result: RotateResult) -> str:
    lines = [
        f"Session : {result.session_name}",
        f"Direction: {result.direction}",
        f"Positions: {result.positions}",
        f"Steps    : {result.step_count}",
    ]
    return "\n".join(lines)
