"""squasher.py — merge consecutive steps with the same command into one."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from breadcrumb.session import Session, Step


class SquashError(Exception):
    pass


@dataclass
class SquashResult:
    session: Session
    original_count: int
    squashed_count: int
    groups_merged: int

    @property
    def summary(self) -> str:
        saved = self.original_count - self.squashed_count
        return (
            f"Squashed {self.original_count} steps → {self.squashed_count} steps "
            f"({saved} removed across {self.groups_merged} merged group(s))."
        )


def squash_session(
    session: Session,
    *,
    case_sensitive: bool = False,
    combine_notes: bool = True,
) -> SquashResult:
    """Merge consecutive steps that share the same command.

    The first step in each run is kept; its note is optionally extended with
    notes from subsequent duplicate steps.
    """
    if not session.steps:
        raise SquashError("Cannot squash a session with no steps.")

    original_count = len(session.steps)
    squashed: List[Step] = []
    groups_merged = 0

    def _key(cmd: str) -> str:
        return cmd if case_sensitive else cmd.lower()

    i = 0
    while i < len(session.steps):
        current = session.steps[i]
        run: List[Step] = [current]
        j = i + 1
        while j < len(session.steps) and _key(session.steps[j].command) == _key(current.command):
            run.append(session.steps[j])
            j += 1

        if len(run) > 1:
            groups_merged += 1
            if combine_notes:
                extra_notes = [
                    s.note for s in run[1:] if s.note and s.note != current.note
                ]
                merged_note = current.note or ""
                for n in extra_notes:
                    if n not in merged_note:
                        merged_note = f"{merged_note}; {n}".lstrip("; ")
                merged = Step(
                    command=current.command,
                    note=merged_note or None,
                    timestamp=current.timestamp,
                    metadata=dict(current.metadata),
                )
            else:
                merged = Step(
                    command=current.command,
                    note=current.note,
                    timestamp=current.timestamp,
                    metadata=dict(current.metadata),
                )
            squashed.append(merged)
        else:
            squashed.append(current)

        i = j

    session.steps = squashed
    return SquashResult(
        session=session,
        original_count=original_count,
        squashed_count=len(squashed),
        groups_merged=groups_merged,
    )
