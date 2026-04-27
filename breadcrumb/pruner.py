"""Pruner: remove steps from a session based on age or count thresholds."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List

from breadcrumb.session import Session, Step


class PruneError(Exception):
    pass


@dataclass
class PruneResult:
    removed: List[Step] = field(default_factory=list)
    kept: List[Step] = field(default_factory=list)

    @property
    def removed_count(self) -> int:
        return len(self.removed)

    @property
    def kept_count(self) -> int:
        return len(self.kept)

    def summary(self) -> str:
        return f"Pruned {self.removed_count} step(s), kept {self.kept_count}."


def prune_older_than(session: Session, days: int) -> PruneResult:
    """Remove steps whose timestamp is older than *days* days ago."""
    if days < 0:
        raise PruneError("days must be a non-negative integer")
    now = datetime.now(tz=timezone.utc)
    result = PruneResult()
    kept: List[Step] = []
    for step in session.steps:
        try:
            ts = datetime.fromisoformat(step.timestamp)
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
        except (ValueError, AttributeError):
            kept.append(step)
            result.kept.append(step)
            continue
        age_days = (now - ts).days
        if age_days > days:
            result.removed.append(step)
        else:
            kept.append(step)
            result.kept.append(step)
    session.steps = kept
    return result


def prune_beyond_count(session: Session, max_steps: int) -> PruneResult:
    """Keep only the *max_steps* most recent steps, removing the rest."""
    if max_steps < 0:
        raise PruneError("max_steps must be a non-negative integer")
    result = PruneResult()
    if len(session.steps) <= max_steps:
        result.kept = list(session.steps)
        return result
    cutoff = len(session.steps) - max_steps
    result.removed = session.steps[:cutoff]
    result.kept = session.steps[cutoff:]
    session.steps = result.kept
    return result


def prune_empty_commands(session: Session) -> PruneResult:
    """Remove steps whose command is blank or whitespace-only."""
    result = PruneResult()
    kept: List[Step] = []
    for step in session.steps:
        if not step.command.strip():
            result.removed.append(step)
        else:
            kept.append(step)
            result.kept.append(step)
    session.steps = kept
    return result
