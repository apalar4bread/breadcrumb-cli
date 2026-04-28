"""Tests for breadcrumb.capper."""

import pytest

from breadcrumb.session import Session, Step
from breadcrumb.capper import cap_session, CapError


def make_session(commands: list[str]) -> Session:
    s = Session(name="test")
    for cmd in commands:
        s.steps.append(Step(command=cmd))
    return s


def test_cap_within_limit_no_change():
    s = make_session(["a", "b", "c"])
    result = cap_session(s, max_steps=5)
    assert result.removed_count == 0
    assert result.kept_count == 3
    assert result.original_count == 3


def test_cap_oldest_removes_from_start():
    s = make_session(["a", "b", "c", "d", "e"])
    result = cap_session(s, max_steps=3, strategy="oldest")
    assert result.removed_count == 2
    assert [st.command for st in s.steps] == ["c", "d", "e"]


def test_cap_newest_removes_from_end():
    s = make_session(["a", "b", "c", "d", "e"])
    result = cap_session(s, max_steps=3, strategy="newest")
    assert result.removed_count == 2
    assert [st.command for st in s.steps] == ["a", "b", "c"]


def test_cap_exactly_at_limit():
    s = make_session(["x", "y", "z"])
    result = cap_session(s, max_steps=3)
    assert result.removed_count == 0
    assert result.kept_count == 3


def test_cap_to_one_step():
    s = make_session(["a", "b", "c"])
    result = cap_session(s, max_steps=1, strategy="newest")
    assert result.kept_count == 1
    assert s.steps[0].command == "a"


def test_cap_invalid_max_steps_raises():
    s = make_session(["a", "b"])
    with pytest.raises(CapError, match="max_steps must be >= 1"):
        cap_session(s, max_steps=0)


def test_cap_negative_max_steps_raises():
    s = make_session(["a"])
    with pytest.raises(CapError):
        cap_session(s, max_steps=-3)


def test_cap_invalid_strategy_raises():
    s = make_session(["a", "b"])
    with pytest.raises(CapError, match="Unknown strategy"):
        cap_session(s, max_steps=1, strategy="random")  # type: ignore


def test_summary_no_removal():
    s = make_session(["a"])
    result = cap_session(s, max_steps=10)
    assert "within cap" in result.summary()


def test_summary_with_removal_oldest():
    s = make_session(["a", "b", "c", "d"])
    result = cap_session(s, max_steps=2, strategy="oldest")
    summary = result.summary()
    assert "start" in summary
    assert "removed 2" in summary


def test_summary_with_removal_newest():
    s = make_session(["a", "b", "c", "d"])
    result = cap_session(s, max_steps=2, strategy="newest")
    summary = result.summary()
    assert "end" in summary
