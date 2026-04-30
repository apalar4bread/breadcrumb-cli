"""Repeater: mark steps to run repeatedly and generate repeated-step sessions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from breadcrumb.session import Session, Step


class RepeatError(Exception):
    pass


@dataclass
class RepeatResult:
    original_count: int
    repeated_count: int
    new_session: Session

    @property
    def summary(self) -> str:
        return (
            f"Repeated {self.repeated_count} step(s) "
            f"from {self.original_count} total into '{self.new_session.name}'."
        )


def mark_repeat(session: Session, index: int, times: int = 2) -> Step:
    """Mark a step to be repeated *times* times. Stores metadata."""
    if times < 2:
        raise RepeatError("times must be >= 2")
    if index < 0 or index >= len(session.steps):
        raise RepeatError(f"Step index {index} out of range")
    step = session.steps[index]
    step.metadata["repeat"] = str(times)
    return step


def clear_repeat(session: Session, index: int) -> Step:
    """Remove repeat marker from a step."""
    if index < 0 or index >= len(session.steps):
        raise RepeatError(f"Step index {index} out of range")
    step = session.steps[index]
    step.metadata.pop("repeat", None)
    return step


def expand_repeats(session: Session, name: Optional[str] = None) -> RepeatResult:
    """Return a new session where marked steps are duplicated inline."""
    if not session.steps:
        raise RepeatError("Cannot expand an empty session")

    new_steps: List[Step] = []
    for step in session.steps:
        times = int(step.metadata.get("repeat", 1))
        for i in range(times):
            import copy
            s = copy.deepcopy(step)
            if i > 0:
                s.metadata.pop("repeat", None)
                s.metadata["repeat_copy"] = "true"
            new_steps.append(s)

    new_name = name or f"{session.name} (expanded)"
    import uuid, datetime
    new_session = Session(
        id=str(uuid.uuid4()),
        name=new_name,
        created_at=datetime.datetime.utcnow().isoformat(),
        steps=new_steps,
        tags=list(session.tags),
        metadata=dict(session.metadata),
    )
    repeated = sum(
        int(s.metadata.get("repeat", 1)) - 1 for s in session.steps
    )
    return RepeatResult(
        original_count=len(session.steps),
        repeated_count=repeated,
        new_session=new_session,
    )
