"""Throttler: limit how many steps can be added to a session within a time window."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List

from breadcrumb.session import Session


class ThrottleError(Exception):
    pass


@dataclass
class ThrottleResult:
    session_name: str
    window_seconds: int
    max_steps: int
    steps_in_window: int
    throttled: bool

    def summary(self) -> str:
        status = "THROTTLED" if self.throttled else "OK"
        return (
            f"[{status}] '{self.session_name}': "
            f"{self.steps_in_window}/{self.max_steps} steps "
            f"in last {self.window_seconds}s window"
        )


def check_throttle(
    session: Session,
    max_steps: int,
    window_seconds: int = 60,
    now: datetime | None = None,
) -> ThrottleResult:
    """Check whether the session has exceeded the step rate limit."""
    if max_steps < 1:
        raise ThrottleError("max_steps must be at least 1")
    if window_seconds < 1:
        raise ThrottleError("window_seconds must be at least 1")

    if now is None:
        now = datetime.utcnow()

    cutoff = now - timedelta(seconds=window_seconds)
    recent: List = []
    for step in session.steps:
        try:
            ts = datetime.fromisoformat(step.timestamp)
        except (ValueError, AttributeError):
            continue
        if ts >= cutoff:
            recent.append(step)

    throttled = len(recent) >= max_steps
    return ThrottleResult(
        session_name=session.name,
        window_seconds=window_seconds,
        max_steps=max_steps,
        steps_in_window=len(recent),
        throttled=throttled,
    )


def assert_not_throttled(
    session: Session,
    max_steps: int,
    window_seconds: int = 60,
    now: datetime | None = None,
) -> ThrottleResult:
    """Raise ThrottleError if the session is throttled."""
    result = check_throttle(session, max_steps, window_seconds, now)
    if result.throttled:
        raise ThrottleError(
            f"Session '{session.name}' is throttled: "
            f"{result.steps_in_window} steps in the last {window_seconds}s "
            f"(limit: {max_steps})"
        )
    return result
