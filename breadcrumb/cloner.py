"""Clone sessions — create a deep copy with a new name and fresh ID."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from breadcrumb.session import Session, Step


class CloneError(Exception):
    pass


def clone_session(session: Session, new_name: Optional[str] = None) -> Session:
    """Return a deep copy of *session* with a new ID and optional new name."""
    if not session.steps and session.steps is not None:
        pass  # allow cloning empty sessions

    name = new_name.strip() if new_name else f"{session.name} (copy)"
    if not name:
        raise CloneError("Cloned session name must not be blank.")
    if len(name) > 120:
        raise CloneError("Cloned session name is too long (max 120 chars).")

    cloned_steps = [
        Step(
            command=step.command,
            note=step.note,
            timestamp=step.timestamp,
            metadata=dict(step.metadata),
        )
        for step in session.steps
    ]

    cloned = Session(
        id=str(uuid.uuid4()),
        name=name,
        created_at=datetime.utcnow().isoformat(),
        steps=cloned_steps,
        tags=list(session.tags),
    )
    return cloned


def clone_steps_only(session: Session, indices: list[int]) -> list[Step]:
    """Return cloned copies of steps at the given indices."""
    result = []
    for i in indices:
        if i < 0 or i >= len(session.steps):
            raise CloneError(f"Step index {i} out of range.")
        s = session.steps[i]
        result.append(
            Step(
                command=s.command,
                note=s.note,
                timestamp=s.timestamp,
                metadata=dict(s.metadata),
            )
        )
    return result
