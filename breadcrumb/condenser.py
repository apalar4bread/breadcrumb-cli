"""condenser.py — collapse a session's steps into a shorter summary session."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from breadcrumb.session import Session, Step, add_step


class CondenserError(Exception):
    pass


@dataclass
class CondenserResult:
    original_count: int
    condensed_count: int
    session: Session

    def summary(self) -> str:
        removed = self.original_count - self.condensed_count
        return (
            f"Condensed {self.original_count} steps → {self.condensed_count} steps "
            f"({removed} removed)"
        )


def condense_session(
    session: Session,
    max_steps: int,
    name: Optional[str] = None,
    strategy: str = "first",
) -> CondenserResult:
    """Return a new session with at most *max_steps* steps.

    strategy:
        'first'  – keep the first N steps
        'last'   – keep the last N steps
        'spread' – evenly sample across all steps
    """
    if max_steps < 1:
        raise CondenserError("max_steps must be at least 1")

    strategy = strategy.lower()
    if strategy not in ("first", "last", "spread"):
        raise CondenserError(f"Unknown strategy '{strategy}'; use first, last, or spread")

    steps: List[Step] = session.steps
    original_count = len(steps)

    if original_count <= max_steps:
        chosen = list(steps)
    elif strategy == "first":
        chosen = steps[:max_steps]
    elif strategy == "last":
        chosen = steps[-max_steps:]
    else:  # spread
        if max_steps == 1:
            chosen = [steps[0]]
        else:
            indices = [
                round(i * (original_count - 1) / (max_steps - 1))
                for i in range(max_steps)
            ]
            chosen = [steps[i] for i in indices]

    new_session = Session(
        id=session.id,
        name=name or session.name,
        tags=list(session.tags),
        metadata=dict(session.metadata),
        steps=[],
    )
    for step in chosen:
        add_step(
            new_session,
            command=step.command,
            note=step.note,
            metadata=dict(step.metadata),
        )

    return CondenserResult(
        original_count=original_count,
        condensed_count=len(new_session.steps),
        session=new_session,
    )
