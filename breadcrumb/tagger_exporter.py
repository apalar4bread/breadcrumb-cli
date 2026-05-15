"""Export tag-related data from sessions to various formats."""

from __future__ import annotations

from typing import List, Dict

from breadcrumb.session import Session
from breadcrumb.tagger import list_tags


class TagExportError(Exception):
    pass


def export_tags_to_dict(sessions: List[Session]) -> Dict[str, List[str]]:
    """Return a mapping of session_id -> list of tags."""
    result: Dict[str, List[str]] = {}
    for session in sessions:
        result[session.id] = list(list_tags(session))
    return result


def export_tags_flat(sessions: List[Session]) -> List[Dict]:
    """Return a flat list of {session_id, session_name, tag} records."""
    rows = []
    for session in sessions:
        for tag in list_tags(session):
            rows.append({
                "session_id": session.id,
                "session_name": session.name,
                "tag": tag,
            })
    return rows


def format_tags_text(sessions: List[Session]) -> str:
    """Format tag data as a human-readable text block."""
    if not sessions:
        return "No sessions."
    lines = []
    for session in sessions:
        tags = list_tags(session)
        tag_str = ", ".join(sorted(tags)) if tags else "(none)"
        lines.append(f"{session.name} [{session.id[:8]}]: {tag_str}")
    return "\n".join(lines)


def all_unique_tags(sessions: List[Session]) -> List[str]:
    """Return a sorted list of all unique tags across all sessions."""
    seen = set()
    for session in sessions:
        for tag in list_tags(session):
            seen.add(tag)
    return sorted(seen)
