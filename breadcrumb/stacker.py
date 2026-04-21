"""stacker.py — push/pop steps between sessions like a stack."""

from dataclasses import dataclass, field
from typing import List, Optional
from breadcrumb.session import Session, Step


class StackError(Exception):
    pass


@dataclass
class StackResult:
    moved_step: Step
    source_session: str
    target_session: str
    remaining_count: int


def push_step(source: Session, target: Session, index: Optional[int] = None) -> StackResult:
    """Move a step from source session onto target session.

    If index is None, pops the last step.
    """
    if not source.steps:
        raise StackError(f"Session '{source.name}' has no steps to push.")

    if index is None:
        index = len(source.steps) - 1

    if index < 0 or index >= len(source.steps):
        raise StackError(
            f"Step index {index} out of range for session '{source.name}' "
            f"({len(source.steps)} steps)."
        )

    step = source.steps.pop(index)
    target.steps.append(step)

    return StackResult(
        moved_step=step,
        source_session=source.name,
        target_session=target.name,
        remaining_count=len(source.steps),
    )


def pop_step(session: Session, index: Optional[int] = None) -> Step:
    """Remove and return a step from the session (default: last step)."""
    if not session.steps:
        raise StackError(f"Session '{session.name}' has no steps to pop.")

    if index is None:
        return session.steps.pop()

    if index < 0 or index >= len(session.steps):
        raise StackError(
            f"Step index {index} out of range for session '{session.name}'."
        )

    return session.steps.pop(index)


def peek_step(session: Session, index: Optional[int] = None) -> Step:
    """Return a step without removing it (default: last step)."""
    if not session.steps:
        raise StackError(f"Session '{session.name}' has no steps.")

    if index is None:
        return session.steps[-1]

    if index < 0 or index >= len(session.steps):
        raise StackError(
            f"Step index {index} out of range for session '{session.name}'."
        )

    return session.steps[index]


def format_stack_result(result: StackResult) -> str:
    cmd = result.moved_step.command
    return (
        f"Pushed '{cmd}' from '{result.source_session}' "
        f"to '{result.target_session}'. "
        f"{result.remaining_count} step(s) remaining in source."
    )
