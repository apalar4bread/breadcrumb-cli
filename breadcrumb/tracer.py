"""tracer.py — traces command lineage across a session's steps."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from breadcrumb.session import Session, Step


class TracerError(Exception):
    pass


@dataclass
class TraceLink:
    step_index: int
    command: str
    note: Optional[str]
    parent_index: Optional[int]  # index of step this was derived from, if any

    def to_dict(self) -> dict:
        return {
            "step_index": self.step_index,
            "command": self.command,
            "note": self.note,
            "parent_index": self.parent_index,
        }


@dataclass
class TraceResult:
    session_name: str
    chain: List[TraceLink] = field(default_factory=list)

    @property
    def length(self) -> int:
        return len(self.chain)


def trace_session(session: Session, keyword: str, case_sensitive: bool = False) -> TraceResult:
    """Build a trace chain of steps whose commands contain *keyword*."""
    if not keyword or not keyword.strip():
        raise TracerError("keyword must not be empty")

    needle = keyword if case_sensitive else keyword.lower()
    result = TraceResult(session_name=session.name)
    prev_index: Optional[int] = None

    for i, step in enumerate(session.steps):
        haystack = step.command if case_sensitive else step.command.lower()
        if needle in haystack:
            link = TraceLink(
                step_index=i,
                command=step.command,
                note=step.note,
                parent_index=prev_index,
            )
            result.chain.append(link)
            prev_index = i

    return result


def format_trace(result: TraceResult) -> str:
    """Return a human-readable representation of a TraceResult."""
    if not result.chain:
        return f"No matching steps found in '{result.session_name}'."

    lines = [f"Trace for session: {result.session_name}", ""]
    for link in result.chain:
        parent = f"  (follows step {link.parent_index})" if link.parent_index is not None else ""
        note_part = f" # {link.note}" if link.note else ""
        lines.append(f"  [{link.step_index}] {link.command}{note_part}{parent}")
    return "\n".join(lines)
