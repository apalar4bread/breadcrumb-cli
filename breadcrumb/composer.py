"""Compose a new session by cherry-picking steps from multiple sessions."""

from dataclasses import dataclass, field
from typing import List, Tuple

from breadcrumb.session import Session, Step, add_step


class ComposeError(Exception):
    pass


@dataclass
class ComposePick:
    session_id: str
    step_index: int


def compose_session(
    sources: List[Tuple[Session, List[int]]],
    name: str,
) -> Session:
    """Build a new session from cherry-picked steps across multiple sessions.

    Args:
        sources: list of (session, [step_indices]) pairs.
        name: name for the composed session.

    Returns:
        A new Session containing the selected steps in order.
    """
    name = name.strip()
    if not name:
        raise ComposeError("Composed session name must not be blank.")

    result = Session(name=name)

    for session, indices in sources:
        for idx in indices:
            if idx < 0 or idx >= len(session.steps):
                raise ComposeError(
                    f"Step index {idx} out of range for session '{session.name}' "
                    f"(has {len(session.steps)} steps)."
                )
            src: Step = session.steps[idx]
            add_step(
                result,
                command=src.command,
                note=src.note,
                metadata=dict(src.metadata),
            )

    if not result.steps:
        raise ComposeError("Cannot compose a session with no steps selected.")

    return result


def compose_summary(result: Session, sources: List[Tuple[Session, List[int]]]) -> str:
    """Return a human-readable summary of the composition."""
    total = sum(len(idxs) for _, idxs in sources)
    src_names = ", ".join(s.name for s, _ in sources)
    return (
        f"Composed '{result.name}' with {total} step(s) "
        f"from {len(sources)} session(s): {src_names}."
    )
