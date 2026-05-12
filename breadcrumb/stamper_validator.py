"""Validates stamp consistency across session steps."""

from dataclasses import dataclass, field
from typing import List
from breadcrumb.session import Session


class StampValidationError(Exception):
    pass


@dataclass
class StampValidationResult:
    session_name: str
    issues: List[str] = field(default_factory=list)
    checked: int = 0

    def __bool__(self) -> bool:
        return len(self.issues) == 0

    @property
    def summary(self) -> str:
        if not self.issues:
            return f"{self.session_name}: all {self.checked} stamps valid"
        return (
            f"{self.session_name}: {len(self.issues)} issue(s) found "
            f"across {self.checked} stamped step(s)"
        )


def validate_stamps(session: Session) -> StampValidationResult:
    """Check that all stamped steps have valid, parseable timestamps."""
    from datetime import datetime

    result = StampValidationResult(session_name=session.name)

    for i, step in enumerate(session.steps):
        raw = step.metadata.get("stamp")
        if raw is None:
            continue
        result.checked += 1
        if not isinstance(raw, str) or not raw.strip():
            result.issues.append(f"Step {i}: stamp is empty or not a string")
            continue
        try:
            datetime.fromisoformat(raw)
        except ValueError:
            result.issues.append(f"Step {i}: stamp '{raw}' is not a valid ISO timestamp")

    return result


def format_stamp_validation(result: StampValidationResult) -> str:
    lines = [result.summary]
    for issue in result.issues:
        lines.append(f"  - {issue}")
    return "\n".join(lines)
