"""Pin/unpin steps within a session for quick reference."""

from breadcrumb.session import Session


class PinError(Exception):
    pass


def pin_step(session: Session, index: int) -> Session:
    """Mark a step as pinned."""
    if index < 0 or index >= len(session.steps):
        raise PinError(f"Step index {index} out of range (0-{len(session.steps) - 1})")
    step = session.steps[index]
    step.metadata["pinned"] = True
    return session


def unpin_step(session: Session, index: int) -> Session:
    """Remove pinned mark from a step."""
    if index < 0 or index >= len(session.steps):
        raise PinError(f"Step index {index} out of range (0-{len(session.steps) - 1})")
    step = session.steps[index]
    step.metadata.pop("pinned", None)
    return session


def list_pinned(session: Session) -> list:
    """Return list of (index, step) tuples for pinned steps."""
    return [
        (i, step)
        for i, step in enumerate(session.steps)
        if step.metadata.get("pinned") is True
    ]


def is_pinned(session: Session, index: int) -> bool:
    """Check if a step is pinned."""
    if index < 0 or index >= len(session.steps):
        raise PinError(f"Step index {index} out of range")
    return session.steps[index].metadata.get("pinned") is True
