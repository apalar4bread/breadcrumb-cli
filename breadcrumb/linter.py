"""Linter for session steps — checks for common style and quality issues."""

from dataclasses import dataclass, field
from typing import List
from breadcrumb.session import Session


LINT_RULES = [
    "no_note",
    "long_command",
    "trailing_whitespace",
    "all_caps_command",
    "duplicate_consecutive",
]

MAX_COMMAND_LENGTH = 120


@dataclass
class LintIssue:
    step_index: int
    rule: str
    message: str

    def __str__(self) -> str:
        return f"Step {self.step_index + 1} [{self.rule}]: {self.message}"


@dataclass
class LintResult:
    session_name: str
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.issues) == 0

    def summary(self) -> str:
        if self.passed:
            return f"'{self.session_name}': no issues found."
        return f"'{self.session_name}': {len(self.issues)} issue(s) found."


def lint_session(session: Session, rules: List[str] = None) -> LintResult:
    active = set(rules) if rules else set(LINT_RULES)
    result = LintResult(session_name=session.name)

    prev_command = None
    for i, step in enumerate(session.steps):
        cmd = step.command

        if "no_note" in active and not step.note:
            result.issues.append(LintIssue(i, "no_note", "Step has no note/description."))

        if "long_command" in active and len(cmd) > MAX_COMMAND_LENGTH:
            result.issues.append(LintIssue(i, "long_command",
                f"Command exceeds {MAX_COMMAND_LENGTH} characters ({len(cmd)})."))

        if "trailing_whitespace" in active and cmd != cmd.strip():
            result.issues.append(LintIssue(i, "trailing_whitespace",
                "Command has leading or trailing whitespace."))

        if "all_caps_command" in active and cmd == cmd.upper() and cmd.isalpha():
            result.issues.append(LintIssue(i, "all_caps_command",
                "Command appears to be all uppercase."))

        if "duplicate_consecutive" in active and prev_command is not None:
            if cmd.strip().lower() == prev_command.strip().lower():
                result.issues.append(LintIssue(i, "duplicate_consecutive",
                    "Command is identical to the previous step."))

        prev_command = cmd

    return result


def format_lint_result(result: LintResult) -> str:
    lines = [result.summary()]
    for issue in result.issues:
        lines.append(f"  {issue}")
    return "\n".join(lines)
