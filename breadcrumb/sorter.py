"""Sort session steps by various criteria."""

from typing import List
from breadcrumb.session import Session, Step


class SortError(ValueError):
    pass


VALID_KEYS = {"timestamp", "command", "note"}


def sort_steps(session: Session, key: str = "timestamp", reverse: bool = False) -> Session:
    """Return a new session with steps sorted by the given key."""
    if key not in VALID_KEYS:
        raise SortError(f"Invalid sort key '{key}'. Choose from: {', '.join(sorted(VALID_KEYS))}")

    def step_key(step: Step):
        if key == "timestamp":
            return step.timestamp
        if key == "command":
            return step.command.lower()
        if key == "note":
            return (step.note or "").lower()
        return ""

    sorted_steps = sorted(session.steps, key=step_key, reverse=reverse)
    new_session = Session(
        id=session.id,
        name=session.name,
        created_at=session.created_at,
        tags=list(session.tags),
        steps=sorted_steps,
        metadata=dict(session.metadata),
    )
    return new_session


def sort_by_command(session: Session, reverse: bool = False) -> Session:
    return sort_steps(session, key="command", reverse=reverse)


def sort_by_timestamp(session: Session, reverse: bool = False) -> Session:
    return sort_steps(session, key="timestamp", reverse=reverse)


def sort_by_note(session: Session, reverse: bool = False) -> Session:
    return sort_steps(session, key="note", reverse=reverse)
