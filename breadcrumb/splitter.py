"""Split a session into two sessions at a given step index."""

from typing import Tuple
from breadcrumb.session import Session, Step


class SplitError(Exception):
    pass


def split_session(
    session: Session,
    at: int,
    name_a: str | None = None,
    name_b: str | None = None,
) -> Tuple[Session, Session]:
    """Split *session* into two at step index *at* (exclusive upper bound for first half).

    Steps [0, at) go into the first session; steps [at, end) into the second.
    """
    steps = session.steps
    if not steps:
        raise SplitError("Cannot split a session with no steps")
    if at <= 0 or at >= len(steps):
        raise SplitError(
            f"Split index {at} is out of range for session with {len(steps)} steps"
        )

    import uuid
    from datetime import datetime, timezone

    def _make(name: str, subset: list[Step]) -> Session:
        s = Session(
            id=str(uuid.uuid4()),
            name=name,
            created_at=datetime.now(timezone.utc).isoformat(),
            steps=list(subset),
            tags=list(session.tags),
        )
        return s

    name_a = name_a or f"{session.name} (part 1)"
    name_b = name_b or f"{session.name} (part 2)"

    session_a = _make(name_a, steps[:at])
    session_b = _make(name_b, steps[at:])
    return session_a, session_b


def split_summary(session_a: Session, session_b: Session) -> str:
    lines = [
        f"Split into:",
        f"  [{session_a.id[:8]}] {session_a.name!r} — {len(session_a.steps)} step(s)",
        f"  [{session_b.id[:8]}] {session_b.name!r} — {len(session_b.steps)} step(s)",
    ]
    return "\n".join(lines)
