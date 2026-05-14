"""fixer.py — automatically fix common step issues in a session."""

from dataclasses import dataclass, field
from typing import List

from breadcrumb.session import Session


class FixError(Exception):
    pass


@dataclass
class FixResult:
    session: Session
    fixes: List[str] = field(default_factory=list)

    @property
    def fix_count(self) -> int:
        return len(self.fixes)

    def summary(self) -> str:
        if not self.fixes:
            return "No fixes applied."
        lines = [f"{self.fix_count} fix(es) applied:"]
        for f in self.fixes:
            lines.append(f"  - {f}")
        return "\n".join(lines)


def fix_session(session: Session, *, strip_whitespace: bool = True,
                remove_empty: bool = True, dedupe_notes: bool = True) -> FixResult:
    """Apply automatic fixes to steps in a session."""
    if not session.id:
        raise FixError("Session must have an id.")

    fixes: List[str] = []
    kept = []

    seen_notes = set()

    for i, step in enumerate(session.steps):
        label = f"step {i + 1} ({step.command!r})"

        if remove_empty and not step.command.strip():
            fixes.append(f"Removed empty command at {label}")
            continue

        if strip_whitespace:
            stripped_cmd = step.command.strip()
            if stripped_cmd != step.command:
                fixes.append(f"Stripped whitespace from command at {label}")
                step.command = stripped_cmd

            if step.note:
                stripped_note = step.note.strip()
                if stripped_note != step.note:
                    fixes.append(f"Stripped whitespace from note at {label}")
                    step.note = stripped_note

        if dedupe_notes and step.note:
            note_key = step.note.lower()
            if note_key in seen_notes:
                fixes.append(f"Cleared duplicate note at {label}")
                step.note = ""
            else:
                seen_notes.add(note_key)

        kept.append(step)

    session.steps = kept
    return FixResult(session=session, fixes=fixes)
