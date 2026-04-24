"""Aliaser: assign short aliases to sessions for quick lookup."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from breadcrumb.session import Session


class AliasError(Exception):
    pass


_ALIAS_META_KEY = "alias"
_MAX_ALIAS_LEN = 32
_VALID_CHARS = set("abcdefghijklmnopqrstuvwxyz0123456789_-")


def _validate_alias(alias: str) -> str:
    alias = alias.strip().lower()
    if not alias:
        raise AliasError("Alias must not be empty.")
    if len(alias) > _MAX_ALIAS_LEN:
        raise AliasError(f"Alias must be {_MAX_ALIAS_LEN} characters or fewer.")
    invalid = set(alias) - _VALID_CHARS
    if invalid:
        raise AliasError(
            f"Alias contains invalid characters: {', '.join(sorted(invalid))}. "
            "Use only letters, digits, hyphens, and underscores."
        )
    return alias


def set_alias(session: Session, alias: str) -> str:
    """Attach a normalised alias to *session*. Returns the alias string."""
    alias = _validate_alias(alias)
    session.metadata[_ALIAS_META_KEY] = alias
    return alias


def clear_alias(session: Session) -> None:
    """Remove the alias from *session* if present."""
    session.metadata.pop(_ALIAS_META_KEY, None)


def get_alias(session: Session) -> Optional[str]:
    """Return the alias for *session*, or None if unset."""
    return session.metadata.get(_ALIAS_META_KEY)


def find_by_alias(sessions: list[Session], alias: str) -> Optional[Session]:
    """Return the first session whose alias matches *alias* (case-insensitive)."""
    alias = alias.strip().lower()
    for s in sessions:
        if get_alias(s) == alias:
            return s
    return None


def list_aliases(sessions: list[Session]) -> Dict[str, str]:
    """Return a mapping of alias -> session name for all aliased sessions."""
    result: Dict[str, str] = {}
    for s in sessions:
        a = get_alias(s)
        if a:
            result[a] = s.name
    return result
