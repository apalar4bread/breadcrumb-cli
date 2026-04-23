"""Mirror module: create a reversed or inverted copy of a session."""

from dataclasses import dataclass, field
from typing import Optional
from breadcrumb.session import Session, Step
import copy


class MirrorError(Exception):
    pass


@dataclass
class MirrorResult:
    original_name: str
    mirrored_name: str
    step_count: int
    reversed: bool


def mirror_session(
    session: Session,
    name: Optional[str] = None,
    reverse: bool = True,
) -> Session:
    """Return a new session that is a mirrored (optionally reversed) copy."""
    if not session.steps:
        raise MirrorError("Cannot mirror a session with no steps.")

    mirrored_name = name or f"{session.name} (mirrored)"
    mirrored_name = mirrored_name.strip()
    if not mirrored_name:
        raise MirrorError("Mirrored session name cannot be blank.")

    new_session = Session(
        id=session.id + "-mirror",
        name=mirrored_name,
        tags=list(session.tags),
        metadata=copy.deepcopy(session.metadata),
    )

    steps = [copy.deepcopy(s) for s in session.steps]
    if reverse:
        steps = list(reversed(steps))

    new_session.steps = steps
    return new_session


def format_mirror_result(result: MirrorResult) -> str:
    direction = "reversed" if result.reversed else "copied"
    return (
        f"Mirrored '{result.original_name}' -> '{result.mirrored_name}' "
        f"({result.step_count} steps, {direction})"
    )
