"""Validates sessions and steps for integrity and completeness."""

from dataclasses import dataclass, field
from typing import List
from breadcrumb.session import Session, Step


@dataclass
class ValidationResult:
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def __bool__(self):
        return self.valid


def validate_step(step: Step) -> ValidationResult:
    errors = []
    warnings = []

    if not step.command or not step.command.strip():
        errors.append("Step command is empty or blank.")

    if len(step.command) > 1000:
        warnings.append("Step command is unusually long (>1000 chars).")

    if step.note and len(step.note) > 500:
        warnings.append("Step note is unusually long (>500 chars).")

    return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)


def validate_session(session: Session) -> ValidationResult:
    errors = []
    warnings = []

    if not session.name or not session.name.strip():
        errors.append("Session name is empty or blank.")

    if not session.id:
        errors.append("Session is missing an ID.")

    if len(session.steps) == 0:
        warnings.append("Session has no steps.")

    for i, step in enumerate(session.steps):
        result = validate_step(step)
        for e in result.errors:
            errors.append(f"Step {i + 1}: {e}")
        for w in result.warnings:
            warnings.append(f"Step {i + 1}: {w}")

    return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)


def format_validation_result(result: ValidationResult) -> str:
    lines = []
    if result.valid:
        lines.append("✓ Validation passed.")
    else:
        lines.append("✗ Validation failed.")
    for e in result.errors:
        lines.append(f"  [ERROR] {e}")
    for w in result.warnings:
        lines.append(f"  [WARN]  {w}")
    return "\n".join(lines)
