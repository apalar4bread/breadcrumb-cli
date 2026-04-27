"""Indexer: build and query a flat index of all steps across sessions."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional

from breadcrumb.session import Session, Step


class IndexError(Exception):
    pass


@dataclass
class IndexEntry:
    session_id: str
    session_name: str
    step_index: int
    command: str
    note: str
    tags: List[str] = field(default_factory=list)
    label: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "session_name": self.session_name,
            "step_index": self.step_index,
            "command": self.command,
            "note": self.note,
            "tags": self.tags,
            "label": self.label,
        }


@dataclass
class StepIndex:
    entries: List[IndexEntry] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.entries)


def build_index(sessions: List[Session]) -> StepIndex:
    """Build a flat index from a list of sessions."""
    entries: List[IndexEntry] = []
    for session in sessions:
        for i, step in enumerate(session.steps):
            entries.append(
                IndexEntry(
                    session_id=session.id,
                    session_name=session.name,
                    step_index=i,
                    command=step.command,
                    note=step.note or "",
                    tags=list(session.metadata.get("tags", [])),
                    label=step.metadata.get("label"),
                )
            )
    return StepIndex(entries=entries)


def query_index(
    index: StepIndex,
    command: Optional[str] = None,
    note: Optional[str] = None,
    session_name: Optional[str] = None,
    case_sensitive: bool = False,
) -> List[IndexEntry]:
    """Filter index entries by optional criteria."""
    results = index.entries
    if command:
        needle = command if case_sensitive else command.lower()
        results = [
            e for e in results
            if (e.command if case_sensitive else e.command.lower()).find(needle) != -1
        ]
    if note:
        needle = note if case_sensitive else note.lower()
        results = [
            e for e in results
            if (e.note if case_sensitive else e.note.lower()).find(needle) != -1
        ]
    if session_name:
        needle = session_name if case_sensitive else session_name.lower()
        results = [
            e for e in results
            if (e.session_name if case_sensitive else e.session_name.lower()).find(needle) != -1
        ]
    return results


def format_index_entry(entry: IndexEntry) -> str:
    parts = [f"[{entry.session_name}] step {entry.step_index + 1}: {entry.command}"]
    if entry.note:
        parts.append(f"  note: {entry.note}")
    if entry.label:
        parts.append(f"  label: {entry.label}")
    return "\n".join(parts)
