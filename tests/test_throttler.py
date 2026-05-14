"""Tests for breadcrumb.throttler."""

from datetime import datetime, timedelta

import pytest

from breadcrumb.session import Session, Step
from breadcrumb.throttler import (
    ThrottleError,
    ThrottleResult,
    assert_not_throttled,
    check_throttle,
)


def _ts(offset_seconds: int = 0) -> str:
    """Return an ISO timestamp relative to a fixed reference time."""
    base = datetime(2024, 6, 1, 12, 0, 0)
    return (base + timedelta(seconds=offset_seconds)).isoformat()


NOW = datetime(2024, 6, 1, 12, 1, 0)  # 60 seconds after base


def make_session(commands, offsets) -> Session:
    session = Session(name="test", id="s1")
    for cmd, off in zip(commands, offsets):
        step = Step(command=cmd, timestamp=_ts(off))
        session.steps.append(step)
    return session


def test_no_steps_not_throttled():
    session = Session(name="empty", id="s0")
    result = check_throttle(session, max_steps=3, window_seconds=60, now=NOW)
    assert result.throttled is False
    assert result.steps_in_window == 0


def test_steps_outside_window_not_counted():
    session = make_session(["ls", "pwd"], [0, 10])  # both >60s before NOW
    result = check_throttle(session, max_steps=2, window_seconds=60, now=NOW)
    assert result.steps_in_window == 0
    assert result.throttled is False


def test_steps_inside_window_counted():
    # offsets 50 and 55 are within 60s of NOW (60s mark)
    session = make_session(["ls", "pwd"], [50, 55])
    result = check_throttle(session, max_steps=3, window_seconds=60, now=NOW)
    assert result.steps_in_window == 2
    assert result.throttled is False


def test_throttled_when_at_limit():
    session = make_session(["ls", "pwd", "echo hi"], [50, 52, 58])
    result = check_throttle(session, max_steps=3, window_seconds=60, now=NOW)
    assert result.throttled is True


def test_throttled_when_exceeds_limit():
    session = make_session(["a", "b", "c", "d"], [50, 52, 55, 59])
    result = check_throttle(session, max_steps=3, window_seconds=60, now=NOW)
    assert result.throttled is True
    assert result.steps_in_window == 4


def test_summary_ok():
    session = make_session(["ls"], [55])
    result = check_throttle(session, max_steps=5, window_seconds=60, now=NOW)
    assert "OK" in result.summary()
    assert "test" in result.summary()


def test_summary_throttled():
    session = make_session(["a", "b", "c"], [50, 52, 58])
    result = check_throttle(session, max_steps=3, window_seconds=60, now=NOW)
    assert "THROTTLED" in result.summary()


def test_assert_not_throttled_passes():
    session = make_session(["ls"], [55])
    result = assert_not_throttled(session, max_steps=5, window_seconds=60, now=NOW)
    assert isinstance(result, ThrottleResult)
    assert not result.throttled


def test_assert_not_throttled_raises():
    session = make_session(["a", "b", "c"], [50, 52, 58])
    with pytest.raises(ThrottleError, match="throttled"):
        assert_not_throttled(session, max_steps=3, window_seconds=60, now=NOW)


def test_invalid_max_steps_raises():
    session = Session(name="x", id="x")
    with pytest.raises(ThrottleError, match="max_steps"):
        check_throttle(session, max_steps=0)


def test_invalid_window_raises():
    session = Session(name="x", id="x")
    with pytest.raises(ThrottleError, match="window_seconds"):
        check_throttle(session, max_steps=5, window_seconds=0)
