"""Flattener: merge all steps from multiple sessions into a single flat list."""

from dataclasses import dataclass, field
from typing import List, Tuple

from breadcrumb.session import Session, Step


class FlattenError(Exception):
    pass


@dataclass
class FlattenResult:
    steps: List[Tuple[str, Step]] = field(default_factory=list)  # (session_name, step)
    source_count: int = 0
    total_steps: int = 0


def flatten_sessions(sessions: List[Session]) -> FlattenResult:
    """Collect every step from each session into one ordered list."""
    if not sessions:
        raise FlattenError("No sessions provided to flatten.")

    result = FlattenResult(source_count=len(sessions))
    for session in sessions:
        for step in session.steps:
            result.steps.append((session.name, step))
    result.total_steps = len(result.steps)
    return result


def flatten_to_session(sessions: List[Session], name: str = "") -> Session:
    """Flatten multiple sessions into a new single Session."""
    if not sessions:
        raise FlattenError("No sessions provided to flatten.")

    import copy
    from breadcrumb.session import Session as Sess

    flat_name = name.strip() if name and name.strip() else "flattened-" + "-".join(
        s.name for s in sessions[:3]
    )
    new_session = Sess(name=flat_name)
    for session in sessions:
        for step in session.steps:
            new_session.steps.append(copy.deepcopy(step))
    return new_session


def format_flatten_result(result: FlattenResult) -> str:
    """Return a human-readable summary of a FlattenResult."""
    lines = [
        f"Flattened {result.source_count} session(s) → {result.total_steps} step(s)",
        "",
    ]
    for idx, (session_name, step) in enumerate(result.steps, 1):
        note_part = f"  # {step.note}" if step.note else ""
        lines.append(f"  {idx:>3}. [{session_name}] {step.command}{note_part}")
    return "\n".join(lines)
