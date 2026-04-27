"""Optimizer: suggests improvements to a session by detecting redundant or suboptimal step patterns."""

from dataclasses import dataclass, field
from typing import List

from breadcrumb.session import Session


class OptimizerError(Exception):
    pass


@dataclass
class Suggestion:
    step_index: int
    command: str
    reason: str
    suggestion: str

    def __str__(self) -> str:
        return f"Step {self.step_index + 1} ({self.command!r}): {self.reason} → {self.suggestion}"


@dataclass
class OptimizeResult:
    session_name: str
    suggestions: List[Suggestion] = field(default_factory=list)

    @property
    def has_suggestions(self) -> bool:
        return len(self.suggestions) > 0


def optimize_session(session: Session) -> OptimizeResult:
    """Analyse a session and return a list of improvement suggestions."""
    if not session.steps:
        raise OptimizerError("Session has no steps to optimize.")

    result = OptimizeResult(session_name=session.name)

    seen_commands: dict = {}

    for idx, step in enumerate(session.steps):
        cmd = step.command.strip()

        # Detect consecutive duplicates
        if idx > 0 and session.steps[idx - 1].command.strip().lower() == cmd.lower():
            result.suggestions.append(Suggestion(
                step_index=idx,
                command=cmd,
                reason="Duplicate of the previous step",
                suggestion="Remove or merge this repeated command",
            ))

        # Detect cd followed immediately by ls (common pattern)
        if cmd.lower().startswith("cd ") and idx + 1 < len(session.steps):
            next_cmd = session.steps[idx + 1].command.strip().lower()
            if next_cmd in ("ls", "ls -la", "ls -l", "ll"):
                result.suggestions.append(Suggestion(
                    step_index=idx,
                    command=cmd,
                    reason="'cd' immediately followed by 'ls' is verbose",
                    suggestion=f"Consider combining: cd <dir> && ls",
                ))

        # Detect commands already seen earlier (non-consecutive)
        normalized = cmd.lower()
        if normalized in seen_commands and (idx - seen_commands[normalized]) > 1:
            result.suggestions.append(Suggestion(
                step_index=idx,
                command=cmd,
                reason=f"Command already used at step {seen_commands[normalized] + 1}",
                suggestion="Consider extracting repeated commands into a variable or alias",
            ))
        else:
            seen_commands[normalized] = idx

    return result


def format_optimize_result(result: OptimizeResult) -> str:
    lines = [f"Optimization report for '{result.session_name}'"]
    if not result.has_suggestions:
        lines.append("  No suggestions — session looks clean!")
    else:
        for s in result.suggestions:
            lines.append(f"  • {s}")
    return "\n".join(lines)
