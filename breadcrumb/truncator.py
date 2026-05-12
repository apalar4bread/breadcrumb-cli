"""truncator.py — truncate long command strings and notes in session steps."""

from dataclasses import dataclass, field
from typing import Optional
from breadcrumb.session import Session, Step


class TruncateError(Exception):
    pass


@dataclass
class TruncateResult:
    session: Session
    truncated_count: int = 0
    affected_indices: list = field(default_factory=list)

    def summary(self) -> str:
        if self.truncated_count == 0:
            return "No steps were truncated."
        indices = ", ".join(str(i) for i in self.affected_indices)
        return f"Truncated {self.truncated_count} step(s) at index(es): {indices}."


DEFAULT_MAX_LENGTH = 80


def _truncate_text(text: str, max_length: int, suffix: str = "...") -> tuple[str, bool]:
    """Return (possibly truncated text, was_truncated)."""
    if len(text) <= max_length:
        return text, False
    cut = max(0, max_length - len(suffix))
    return text[:cut] + suffix, True


def truncate_session(
    session: Session,
    max_length: int = DEFAULT_MAX_LENGTH,
    truncate_commands: bool = True,
    truncate_notes: bool = True,
    suffix: str = "...",
) -> TruncateResult:
    """Truncate command and/or note fields on all steps in-place."""
    if max_length < 1:
        raise TruncateError(f"max_length must be at least 1, got {max_length}")
    if not truncate_commands and not truncate_notes:
        raise TruncateError("At least one of truncate_commands or truncate_notes must be True")

    truncated_count = 0
    affected_indices = []

    for idx, step in enumerate(session.steps):
        changed = False

        if truncate_commands:
            new_cmd, was_cut = _truncate_text(step.command, max_length, suffix)
            if was_cut:
                step.command = new_cmd
                changed = True

        if truncate_notes and step.note:
            new_note, was_cut = _truncate_text(step.note, max_length, suffix)
            if was_cut:
                step.note = new_note
                changed = True

        if changed:
            truncated_count += 1
            affected_indices.append(idx)

    return TruncateResult(
        session=session,
        truncated_count=truncated_count,
        affected_indices=affected_indices,
    )
