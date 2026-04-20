"""Redact sensitive patterns from step commands and notes."""

import re
from dataclasses import dataclass, field
from typing import List, Optional

from breadcrumb.session import Session, Step

DEFAULT_PATTERNS = [
    r"(?i)(password|passwd|pwd)\s*=\s*\S+",
    r"(?i)(token|api[_-]?key|secret)\s*=\s*\S+",
    r"(?i)--password\s+\S+",
    r"(?i)--token\s+\S+",
    r"Bearer\s+[A-Za-z0-9\-._~+/]+=*",
]

REDACT_PLACEHOLDER = "[REDACTED]"


class RedactError(Exception):
    pass


@dataclass
class RedactResult:
    original_command: str
    redacted_command: str
    original_note: Optional[str]
    redacted_note: Optional[str]
    changed: bool


def redact_text(text: str, patterns: List[str]) -> str:
    """Apply all patterns to a string and replace matches with placeholder."""
    result = text
    for pattern in patterns:
        result = re.sub(pattern, REDACT_PLACEHOLDER, result)
    return result


def redact_step(step: Step, patterns: Optional[List[str]] = None) -> RedactResult:
    """Return a RedactResult describing what changed (does not mutate step)."""
    pats = patterns if patterns is not None else DEFAULT_PATTERNS
    new_cmd = redact_text(step.command, pats)
    new_note = redact_text(step.note, pats) if step.note else step.note
    changed = new_cmd != step.command or new_note != step.note
    return RedactResult(
        original_command=step.command,
        redacted_command=new_cmd,
        original_note=step.note,
        redacted_note=new_note,
        changed=changed,
    )


def redact_session(
    session: Session, patterns: Optional[List[str]] = None, in_place: bool = False
) -> Session:
    """Return a new session (or mutate in_place) with sensitive data redacted."""
    pats = patterns if patterns is not None else DEFAULT_PATTERNS
    target = session if in_place else Session(
        id=session.id,
        name=session.name,
        steps=[],
        tags=list(session.tags),
        metadata=dict(session.metadata),
    )
    if not in_place:
        for step in session.steps:
            result = redact_step(step, pats)
            target.steps.append(
                Step(
                    command=result.redacted_command,
                    note=result.redacted_note,
                    timestamp=step.timestamp,
                    metadata=dict(step.metadata),
                )
            )
    else:
        for step in target.steps:
            result = redact_step(step, pats)
            step.command = result.redacted_command
            step.note = result.redacted_note
    return target
