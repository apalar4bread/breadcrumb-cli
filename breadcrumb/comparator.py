"""Compare two sessions and produce a human-readable similarity report."""
from dataclasses import dataclass, field
from typing import List
from breadcrumb.session import Session


@dataclass
class CompareResult:
    session_a: str
    session_b: str
    common_commands: List[str] = field(default_factory=list)
    only_in_a: List[str] = field(default_factory=list)
    only_in_b: List[str] = field(default_factory=list)
    similarity_pct: float = 0.0


def compare_sessions(a: Session, b: Session) -> CompareResult:
    cmds_a = {s.command.strip().lower() for s in a.steps if s.command.strip()}
    cmds_b = {s.command.strip().lower() for s in b.steps if s.command.strip()}

    common = sorted(cmds_a & cmds_b)
    only_a = sorted(cmds_a - cmds_b)
    only_b = sorted(cmds_b - cmds_a)

    total = len(cmds_a | cmds_b)
    similarity = round(len(common) / total * 100, 1) if total else 100.0

    return CompareResult(
        session_a=a.name,
        session_b=b.name,
        common_commands=common,
        only_in_a=only_a,
        only_in_b=only_b,
        similarity_pct=similarity,
    )


def format_compare(result: CompareResult) -> str:
    lines = [
        f"Comparing '{result.session_a}' vs '{result.session_b}'",
        f"Similarity: {result.similarity_pct}%",
        f"Common commands ({len(result.common_commands)}): {', '.join(result.common_commands) or 'none'}",
        f"Only in '{result.session_a}' ({len(result.only_in_a)}): {', '.join(result.only_in_a) or 'none'}",
        f"Only in '{result.session_b}' ({len(result.only_in_b)}): {', '.join(result.only_in_b) or 'none'}",
    ]
    return "\n".join(lines)
