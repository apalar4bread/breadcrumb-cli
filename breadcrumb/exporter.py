"""Export sessions to shell scripts, including step annotations as comments."""

from breadcrumb.session import Session, Step
import os


def export_to_script(session: Session) -> str:
    """Generate a shell script string from a session's steps."""
    lines = ["#!/usr/bin/env bash", f"# Session: {session.name}", ""]
    for i, step in enumerate(session.steps):
        comment = step.metadata.get("comment")
        note = step.note
        if comment:
            lines.append(f"# [{i}] {comment}")
        elif note:
            lines.append(f"# [{i}] {note}")
        lines.append(step.command)
        lines.append("")
    return "\n".join(lines)


def write_script(session: Session, path: str) -> None:
    """Write the session script to a file and make it executable."""
    content = export_to_script(session)
    with open(path, "w") as f:
        f.write(content)
    os.chmod(path, 0o755)
