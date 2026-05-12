"""Normalize step commands and notes in a session."""

from dataclasses import dataclass, field
from typing import List

from breadcrumb.session import Session, Step


class NormalizeError(Exception):
    pass


@dataclass
class NormalizeResult:
    session: Session
    changes: List[str] = field(default_factory=list)

    @property
    def change_count(self) -> int:
        return len(self.changes)

    def summary(self) -> str:
        if not self.changes:
            return "No changes made."
        return f"{self.change_count} change(s) applied."


def _normalize_command(cmd: str) -> str:
    """Strip leading/trailing whitespace and collapse internal spaces."""
    return " ".join(cmd.split())


def _normalize_note(note: str) -> str:
    """Strip whitespace from note."""
    return note.strip()


def normalize_session(
    session: Session,
    commands: bool = True,
    notes: bool = True,
) -> NormalizeResult:
    """Normalize commands and/or notes across all steps."""
    if not session.steps:
        return NormalizeResult(session=session)

    changes: List[str] = []

    for i, step in enumerate(session.steps):
        if commands:
            normalized_cmd = _normalize_command(step.command)
            if normalized_cmd != step.command:
                changes.append(
                    f"Step {i + 1}: command '{step.command}' -> '{normalized_cmd}'"
                )
                step.command = normalized_cmd

        if notes and step.note:
            normalized_note = _normalize_note(step.note)
            if normalized_note != step.note:
                changes.append(
                    f"Step {i + 1}: note trimmed"
                )
                step.note = normalized_note

    return NormalizeResult(session=session, changes=changes)
