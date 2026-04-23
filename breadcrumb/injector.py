"""Injector: insert steps into a session at a specific position."""

from dataclasses import dataclass
from typing import Optional

from breadcrumb.session import Session, Step, add_step


class InjectError(Exception):
    pass


@dataclass
class InjectResult:
    session: Session
    inserted_at: int
    command: str


def inject_step(
    session: Session,
    position: int,
    command: str,
    note: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> InjectResult:
    """Insert a new step at *position* (0-based). Existing steps shift right."""
    if not command or not command.strip():
        raise InjectError("Command must not be empty.")

    steps = session.steps
    n = len(steps)

    if position < 0 or position > n:
        raise InjectError(
            f"Position {position} is out of range for session with {n} step(s). "
            f"Valid range: 0..{n}."
        )

    # Build a temporary session to create a properly timestamped Step
    tmp = Session(id=session.id, name=session.name)
    add_step(tmp, command.strip(), note=note, metadata=metadata or {})
    new_step: Step = tmp.steps[0]

    session.steps.insert(position, new_step)
    return InjectResult(session=session, inserted_at=position, command=new_step.command)


def inject_after(
    session: Session,
    position: int,
    command: str,
    note: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> InjectResult:
    """Convenience wrapper: insert *after* position (i.e. at position + 1)."""
    return inject_step(session, position + 1, command, note=note, metadata=metadata)


def format_inject_result(result: InjectResult) -> str:
    return (
        f"Injected '{result.command}' at position {result.inserted_at} "
        f"({len(result.session.steps)} step(s) total)."
    )
