"""Expander: expand abbreviated or aliased commands in session steps."""

from dataclasses import dataclass, field
from typing import Dict, List
from breadcrumb.session import Session


class ExpandError(Exception):
    pass


@dataclass
class ExpandResult:
    session: Session
    expanded: List[int] = field(default_factory=list)  # step indices that were expanded

    @property
    def expand_count(self) -> int:
        return len(self.expanded)

    def summary(self) -> str:
        if self.expand_count == 0:
            return "No commands were expanded."
        return f"{self.expand_count} command(s) expanded."


def expand_steps(session: Session, aliases: Dict[str, str], case_sensitive: bool = False) -> ExpandResult:
    """Replace aliased commands in steps with their full expansions.

    Args:
        session: The session whose steps will be expanded.
        aliases: Mapping of alias -> full command string.
        case_sensitive: If False, alias matching ignores case.

    Returns:
        ExpandResult with the modified session and list of changed indices.
    """
    if not aliases:
        raise ExpandError("Alias map must not be empty.")

    lookup: Dict[str, str] = (
        aliases if case_sensitive else {k.lower(): v for k, v in aliases.items()}
    )

    expanded_indices: List[int] = []

    for idx, step in enumerate(session.steps):
        key = step.command if case_sensitive else step.command.lower()
        if key in lookup:
            step.command = lookup[key]
            expanded_indices.append(idx)

    return ExpandResult(session=session, expanded=expanded_indices)


def build_alias_map(pairs: List[str]) -> Dict[str, str]:
    """Parse a list of 'alias=expansion' strings into a dict.

    Raises ExpandError on malformed entries.
    """
    result: Dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            raise ExpandError(f"Invalid alias entry (expected 'alias=expansion'): {pair!r}")
        alias, _, expansion = pair.partition("=")
        alias = alias.strip()
        expansion = expansion.strip()
        if not alias:
            raise ExpandError("Alias key must not be blank.")
        if not expansion:
            raise ExpandError(f"Expansion for alias {alias!r} must not be blank.")
        result[alias] = expansion
    return result
