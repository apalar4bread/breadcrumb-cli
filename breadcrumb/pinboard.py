"""Pinboard: collect all pinned steps across sessions into a single view."""
from dataclasses import dataclass, field
from typing import List, Tuple
from breadcrumb.session import Session, Step


class PinboardError(Exception):
    pass


@dataclass
class PinboardEntry:
    session_id: str
    session_name: str
    step_index: int
    step: Step

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "session_name": self.session_name,
            "step_index": self.step_index,
            "step": self.step.to_dict(),
        }


def collect_pinned(sessions: List[Session]) -> List[PinboardEntry]:
    """Gather all pinned steps from a list of sessions."""
    entries: List[PinboardEntry] = []
    for session in sessions:
        for i, step in enumerate(session.steps):
            if step.metadata.get("pinned"):
                entries.append(
                    PinboardEntry(
                        session_id=session.id,
                        session_name=session.name,
                        step_index=i,
                        step=step,
                    )
                )
    return entries


def format_pinboard(entries: List[PinboardEntry], verbose: bool = False) -> str:
    if not entries:
        return "No pinned steps found."
    lines = []
    for e in entries:
        line = f"[{e.session_name}] #{e.step_index}  {e.step.command}"
        if e.step.note and verbose:
            line += f"  # {e.step.note}"
        lines.append(line)
    return "\n".join(lines)


def pinboard_summary(entries: List[PinboardEntry]) -> dict:
    sessions_with_pins = {e.session_id for e in entries}
    return {
        "total_pinned": len(entries),
        "sessions_with_pins": len(sessions_with_pins),
    }
