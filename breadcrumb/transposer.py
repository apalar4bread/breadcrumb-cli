"""Transpose (swap) two steps within a session by index."""

from dataclasses import dataclass
from breadcrumb.session import Session


class TransposeError(Exception):
    pass


@dataclass
class TransposeResult:
    session: Session
    index_a: int
    index_b: int
    command_a: str
    command_b: str


def transpose_steps(session: Session, index_a: int, index_b: int) -> TransposeResult:
    """Swap the steps at index_a and index_b in-place. Returns a TransposeResult."""
    n = len(session.steps)
    if n == 0:
        raise TransposeError("Session has no steps.")
    if not (0 <= index_a < n):
        raise TransposeError(f"Index {index_a} is out of range (0-{n - 1}).")
    if not (0 <= index_b < n):
        raise TransposeError(f"Index {index_b} is out of range (0-{n - 1}).")
    if index_a == index_b:
        raise TransposeError("Indices must be different to transpose.")

    cmd_a = session.steps[index_a].command
    cmd_b = session.steps[index_b].command

    session.steps[index_a], session.steps[index_b] = (
        session.steps[index_b],
        session.steps[index_a],
    )

    return TransposeResult(
        session=session,
        index_a=index_a,
        index_b=index_b,
        command_a=cmd_a,
        command_b=cmd_b,
    )


def format_transpose_result(result: TransposeResult) -> str:
    lines = [
        f"Swapped steps {result.index_a} and {result.index_b}:",
        f"  [{result.index_a}] was: {result.command_a!r}  →  now: {result.command_b!r}",
        f"  [{result.index_b}] was: {result.command_b!r}  →  now: {result.command_a!r}",
    ]
    return "\n".join(lines)
