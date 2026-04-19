"""Lock/unlock sessions to prevent accidental modification."""

from breadcrumb.session import Session

LOCK_KEY = "locked"


class LockError(Exception):
    pass


def lock_session(session: Session) -> Session:
    """Mark a session as locked."""
    if is_locked(session):
        raise LockError(f"Session '{session.name}' is already locked.")
    session.metadata[LOCK_KEY] = True
    return session


def unlock_session(session: Session) -> Session:
    """Remove the lock from a session."""
    if not is_locked(session):
        raise LockError(f"Session '{session.name}' is not locked.")
    session.metadata.pop(LOCK_KEY, None)
    return session


def is_locked(session: Session) -> bool:
    """Return True if the session is locked."""
    return bool(session.metadata.get(LOCK_KEY, False))


def assert_unlocked(session: Session) -> None:
    """Raise LockError if the session is locked."""
    if is_locked(session):
        raise LockError(
            f"Session '{session.name}' is locked and cannot be modified. "
            "Unlock it first with `breadcrumb lock unlock <session>`."
        )


def list_locked(sessions: list[Session]) -> list[Session]:
    """Return only locked sessions from a list."""
    return [s for s in sessions if is_locked(s)]
