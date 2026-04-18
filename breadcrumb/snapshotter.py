"""Snapshot a session at a point in time (by step index)."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional
from breadcrumb.session import Session, Step


class SnapshotError(ValueError):
    pass


@dataclass
class Snapshot:
    session_id: str
    session_name: str
    taken_at: str
    step_index: int  # inclusive upper bound
    steps: List[Step] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "session_name": self.session_name,
            "taken_at": self.taken_at,
            "step_index": self.step_index,
            "steps": [s.to_dict() for s in self.steps],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Snapshot":
        steps = [Step.from_dict(s) for s in d.get("steps", [])]
        return cls(
            session_id=d["session_id"],
            session_name=d["session_name"],
            taken_at=d["taken_at"],
            step_index=d["step_index"],
            steps=steps,
        )


def take_snapshot(session: Session, up_to: Optional[int] = None) -> Snapshot:
    """Snapshot session steps up to and including `up_to` index (0-based)."""
    if not session.steps:
        raise SnapshotError("Cannot snapshot a session with no steps.")
    max_idx = len(session.steps) - 1
    if up_to is None:
        up_to = max_idx
    if up_to < 0 or up_to > max_idx:
        raise SnapshotError(f"step index {up_to} out of range 0-{max_idx}.")
    taken_at = datetime.now(timezone.utc).isoformat()
    return Snapshot(
        session_id=session.id,
        session_name=session.name,
        taken_at=taken_at,
        step_index=up_to,
        steps=list(session.steps[: up_to + 1]),
    )


def restore_snapshot(snapshot: Snapshot, target: Session) -> Session:
    """Return a new Session with steps replaced by those from the snapshot."""
    import copy
    restored = copy.deepcopy(target)
    restored.steps = list(snapshot.steps)
    return restored
