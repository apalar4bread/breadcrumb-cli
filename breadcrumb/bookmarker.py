"""Bookmark specific steps for quick reference."""

from breadcrumb.session import Session

BOOKMARK_KEY = "bookmarked"


class BookmarkError(Exception):
    pass


def bookmark_step(session: Session, step_index: int) -> Session:
    """Mark a step as bookmarked."""
    if step_index < 0 or step_index >= len(session.steps):
        raise BookmarkError(f"Step index {step_index} out of range.")
    session.steps[step_index].metadata[BOOKMARK_KEY] = True
    return session


def unbookmark_step(session: Session, step_index: int) -> Session:
    """Remove bookmark from a step."""
    if step_index < 0 or step_index >= len(session.steps):
        raise BookmarkError(f"Step index {step_index} out of range.")
    session.steps[step_index].metadata.pop(BOOKMARK_KEY, None)
    return session


def is_bookmarked(session: Session, step_index: int) -> bool:
    """Return True if the step is bookmarked."""
    if step_index < 0 or step_index >= len(session.steps):
        raise BookmarkError(f"Step index {step_index} out of range.")
    return bool(session.steps[step_index].metadata.get(BOOKMARK_KEY, False))


def list_bookmarked(session: Session) -> list:
    """Return list of (index, step) tuples for all bookmarked steps."""
    return [
        (i, step)
        for i, step in enumerate(session.steps)
        if step.metadata.get(BOOKMARK_KEY)
    ]
