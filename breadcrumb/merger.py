"""Merge two sessions into one combined session."""

from typing import Optional
from breadcrumb.session import Session, Step
import uuid
from datetime import datetime


def merge_sessions(
    base: Session,
    other: Session,
    name: Optional[str] = None,
    skip_duplicates: bool = False,
) -> Session:
    """Merge steps from `other` into `base`, returning a new Session."""
    merged_name = name or f"{base.name}+{other.name}"
    merged = Session(
        id=str(uuid.uuid4()),
        name=merged_name,
        created_at=datetime.utcnow().isoformat(),
        steps=[],
        tags=sorted(set(base.tags) | set(other.tags)),
    )

    seen_commands: set[str] = set()

    for step in base.steps + other.steps:
        if skip_duplicates:
            if step.command in seen_commands:
                continue
            seen_commands.add(step.command)
        merged.steps.append(
            Step(
                command=step.command,
                note=step.note,
                timestamp=step.timestamp,
                metadata=dict(step.metadata),
            )
        )

    return merged


def merge_summary(base: Session, other: Session, merged: Session) -> str:
    """Return a human-readable summary of the merge operation."""
    lines = [
        f"Merged '{base.name}' ({len(base.steps)} steps) + '{other.name}' ({len(other.steps)} steps)",
        f"Result : '{merged.name}' — {len(merged.steps)} steps, tags: {merged.tags or 'none'}",
    ]
    return "\n".join(lines)
