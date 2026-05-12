"""recycler.py — soft-delete and restore sessions."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List

from breadcrumb.session import Session


class RecycleError(Exception):
    pass


@dataclass
class RecycleEntry:
    session: Session
    deleted_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    reason: str = ""

    def to_dict(self) -> dict:
        return {
            "session": self.session.to_dict(),
            "deleted_at": self.deleted_at,
            "reason": self.reason,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RecycleEntry":
        return cls(
            session=Session.from_dict(data["session"]),
            deleted_at=data.get("deleted_at", ""),
            reason=data.get("reason", ""),
        )


def recycle_session(session: Session, reason: str = "") -> RecycleEntry:
    """Create a RecycleEntry for a session (soft-delete)."""
    if not session.id:
        raise RecycleError("Session must have an id to be recycled.")
    return RecycleEntry(session=session, reason=reason.strip())


def restore_session(entry: RecycleEntry) -> Session:
    """Return the session from a RecycleEntry."""
    return entry.session


def format_recycle_entry(entry: RecycleEntry) -> str:
    lines = [
        f"Session : {entry.session.name} ({entry.session.id})",
        f"Deleted : {entry.deleted_at}",
    ]
    if entry.reason:
        lines.append(f"Reason  : {entry.reason}")
    return "\n".join(lines)


def format_recycle_list(entries: List[RecycleEntry]) -> str:
    if not entries:
        return "Recycle bin is empty."
    parts = []
    for i, e in enumerate(entries, 1):
        parts.append(f"{i}. {e.session.name} — deleted {e.deleted_at}")
    return "\n".join(parts)
