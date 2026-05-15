"""Classify steps into categories based on command patterns."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from breadcrumb.session import Session, Step

KNOWN_CATEGORIES = {
    "git": ["git "],
    "docker": ["docker ", "docker-compose "],
    "file": ["cp ", "mv ", "rm ", "mkdir ", "touch ", "ls ", "find "],
    "network": ["curl ", "wget ", "ssh ", "scp ", "ping "],
    "package": ["pip ", "npm ", "apt ", "brew ", "yarn "],
    "python": ["python ", "python3 ", "pytest ", "mypy "],
    "shell": ["echo ", "export ", "source ", "cd ", "cat ", "grep ", "awk ", "sed "],
}


class ClassifyError(Exception):
    pass


@dataclass
class ClassifyResult:
    session_id: str
    categories: Dict[str, List[int]] = field(default_factory=dict)
    uncategorized: List[int] = field(default_factory=list)

    @property
    def total_classified(self) -> int:
        return sum(len(v) for v in self.categories.values())

    def summary(self) -> str:
        lines = [f"Classified {self.total_classified} step(s), {len(self.uncategorized)} uncategorized."]
        for cat, indices in sorted(self.categories.items()):
            lines.append(f"  {cat}: {len(indices)} step(s)")
        return "\n".join(lines)


def classify_step(step: Step) -> str:
    """Return a category name for a step, or 'other' if unrecognized."""
    cmd = step.command.strip().lower()
    for category, prefixes in KNOWN_CATEGORIES.items():
        for prefix in prefixes:
            if cmd.startswith(prefix.lower()) or cmd == prefix.strip().lower():
                return category
    return "other"


def classify_session(session: Session) -> ClassifyResult:
    """Classify all steps in a session by command category."""
    if not session.steps:
        raise ClassifyError(f"Session '{session.name}' has no steps to classify.")

    result = ClassifyResult(session_id=session.id)
    for i, step in enumerate(session.steps):
        category = classify_step(step)
        if category == "other":
            result.uncategorized.append(i)
        else:
            result.categories.setdefault(category, []).append(i)
    return result
