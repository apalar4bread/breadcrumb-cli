"""Formatting utilities for displaying sessions and steps in the terminal."""

from datetime import datetime
from breadcrumb.session import Session, Step


DIVIDER = "-" * 50


def format_step(step: Step, index: int) -> str:
    """Format a single step for display."""
    ts = datetime.fromisoformat(step.timestamp).strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        f"  [{index}] {step.command}",
        f"       dir : {step.cwd}",
        f"       time: {ts}",
    ]
    if step.metadata:
        for key, val in step.metadata.items():
            lines.append(f"       {key}: {val}")
    return "\n".join(lines)


def format_session(session: Session, verbose: bool = False) -> str:
    """Format a session summary or full detail."""
    created = datetime.fromisoformat(session.created_at).strftime("%Y-%m-%d %H:%M:%S")
    header = f"Session : {session.name}\nCreated : {created}\nSteps   : {len(session.steps)}"

    if not verbose or not session.steps:
        return header

    step_lines = []
    for i, step in enumerate(session.steps):
        step_lines.append(format_step(step, i + 1))

    return header + "\n" + DIVIDER + "\n" + "\n".join(step_lines)


def format_session_list(sessions: list) -> str:
    """Format a list of session names for display."""
    if not sessions:
        return "No sessions found."
    lines = [f"  {i + 1}. {name}" for i, name in enumerate(sessions)]
    return "Sessions:\n" + "\n".join(lines)
