"""Utilities for renaming sessions and steps."""

from datetime import datetime
from breadcrumb.session import Session


class RenameError(Exception):
    pass


def rename_session(session: Session, new_name: str) -> Session:
    """Return a copy of the session with a new name."""
    new_name = new_name.strip()
    if not new_name:
        raise RenameError("Session name cannot be blank.")
    if len(new_name) > 128:
        raise RenameError("Session name too long (max 128 characters).")
    session.name = new_name
    session.updated_at = datetime.utcnow().isoformat()
    return session


def rename_step_note(session: Session, step_index: int, new_note: str) -> Session:
    """Replace the note on a specific step (0-based index)."""
    if step_index < 0 or step_index >= len(session.steps):
        raise RenameError(
            f"Step index {step_index} out of range (session has {len(session.steps)} steps)."
        )
    session.steps[step_index].metadata["note"] = new_note.strip()
    session.updated_at = datetime.utcnow().isoformat()
    return session


def rename_step_command(session: Session, step_index: int, new_command: str) -> Session:
    """Replace the command on a specific step (0-based index)."""
    new_command = new_command.strip()
    if not new_command:
        raise RenameError("Step command cannot be blank.")
    if step_index < 0 or step_index >= len(session.steps):
        raise RenameError(
            f"Step index {step_index} out of range (session has {len(session.steps)} steps)."
        )
    session.steps[step_index].command = new_command
    session.updated_at = datetime.utcnow().isoformat()
    return session
