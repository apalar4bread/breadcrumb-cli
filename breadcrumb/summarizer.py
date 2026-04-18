"""Summarize sessions into human-readable stats."""
from breadcrumb.session import Session
from typing import List
from collections import Counter


def summarize_session(session: Session) -> dict:
    """Return a stats dict for a single session."""
    commands = [step.command for step in session.steps]
    notes = [step.note for step in session.steps if step.note]
    tags = list(session.tags) if hasattr(session, "tags") else []

    return {
        "name": session.name,
        "id": session.id,
        "step_count": len(session.steps),
        "unique_commands": len(set(commands)),
        "most_common_command": Counter(commands).most_common(1)[0] if commands else None,
        "notes_count": len(notes),
        "tags": tags,
        "created_at": session.created_at,
    }


def summarize_all(sessions: List[Session]) -> List[dict]:
    """Return summaries for a list of sessions."""
    return [summarize_session(s) for s in sessions]


def format_summary(summary: dict) -> str:
    """Format a single session summary for display."""
    lines = [
        f"Session : {summary['name']} ({summary['id']})",
        f"Created : {summary['created_at']}",
        f"Steps   : {summary['step_count']} ({summary['unique_commands']} unique commands)",
    ]
    if summary["most_common_command"]:
        cmd, count = summary["most_common_command"]
        lines.append(f"Top cmd : {cmd!r} x{count}")
    if summary["notes_count"]:
        lines.append(f"Notes   : {summary['notes_count']}")
    if summary["tags"]:
        lines.append(f"Tags    : {', '.join(summary['tags'])}")
    return "\n".join(lines)
