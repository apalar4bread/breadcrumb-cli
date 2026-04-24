"""stamper.py — attach and query time-based stamps on steps."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from breadcrumb.session import Session, Step

_STAMP_KEY = "stamped_at"
_STAMP_LABEL_KEY = "stamp_label"


class StampError(Exception):
    pass


def stamp_step(
    session: Session,
    index: int,
    label: str = "",
    *,
    at: Optional[datetime] = None,
) -> Step:
    """Attach a timestamp (and optional label) to step *index*."""
    if not (0 <= index < len(session.steps)):
        raise StampError(f"Step index {index} out of range.")
    label = label.strip()
    step = session.steps[index]
    ts = (at or datetime.now(timezone.utc)).isoformat()
    step.metadata[_STAMP_KEY] = ts
    if label:
        step.metadata[_STAMP_LABEL_KEY] = label
    elif _STAMP_LABEL_KEY in step.metadata:
        del step.metadata[_STAMP_LABEL_KEY]
    return step


def clear_stamp(session: Session, index: int) -> Step:
    """Remove stamp metadata from step *index*."""
    if not (0 <= index < len(session.steps)):
        raise StampError(f"Step index {index} out of range.")
    step = session.steps[index]
    step.metadata.pop(_STAMP_KEY, None)
    step.metadata.pop(_STAMP_LABEL_KEY, None)
    return step


def get_stamp(step: Step) -> Optional[str]:
    """Return the ISO timestamp string if the step has been stamped."""
    return step.metadata.get(_STAMP_KEY)


def is_stamped(step: Step) -> bool:
    return _STAMP_KEY in step.metadata


def list_stamped(session: Session) -> list[tuple[int, Step]]:
    """Return (index, step) pairs for every stamped step."""
    return [
        (i, s) for i, s in enumerate(session.steps) if is_stamped(s)
    ]
