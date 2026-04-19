"""Generates human-readable narrations of session steps."""

from dataclasses import dataclass
from typing import List
from breadcrumb.session import Session, Step


class NarratorError(Exception):
    pass


@dataclass
class NarrationLine:
    index: int
    text: str


def _narrate_step(index: int, step: Step) -> str:
    parts = [f"Step {index + 1}: Run `{step.command}`"]
    if step.note:
        parts.append(f"— {step.note}")
    meta = step.metadata or {}
    if meta.get("pinned"):
        parts.append("[pinned]")
    if meta.get("bookmarked"):
        parts.append("[bookmarked]")
    if meta.get("annotation"):
        parts.append(f"(note: {meta['annotation']})")
    if meta.get("label"):
        parts.append(f"[label:{meta['label']}]")
    return " ".join(parts)


def narrate_session(session: Session) -> List[NarrationLine]:
    if not session.steps:
        raise NarratorError("Session has no steps to narrate.")
    return [
        NarrationLine(index=i, text=_narrate_step(i, step))
        for i, step in enumerate(session.steps)
    ]


def format_narration(lines: List[NarrationLine], title: str = "") -> str:
    out = []
    if title:
        out.append(f"# {title}")
        out.append("")
    for line in lines:
        out.append(line.text)
    return "\n".join(out)
