"""Tests for breadcrumb/drainer.py"""

import pytest
from breadcrumb.session import Session, Step
from breadcrumb.drainer import (
    DrainError,
    DrainResult,
    drain_next,
    drain_last,
    drain_at,
    drain_all,
)


def make_session(commands: list[str]) -> Session:
    s = Session(id="s1", name="test")
    for cmd in commands:
        s.steps.append(Step(command=cmd))
    return s


def test_drain_next_removes_first_step():
    s = make_session(["echo a", "echo b", "echo c"])
    result = drain_next(s)
    assert result.step.command == "echo a"
    assert result.index == 0
    assert result.remaining == 2
    assert len(s.steps) == 2
    assert s.steps[0].command == "echo b"


def test_drain_next_empty_raises():
    s = make_session([])
    with pytest.raises(DrainError, match="no steps"):
        drain_next(s)


def test_drain_last_removes_last_step():
    s = make_session(["echo a", "echo b", "echo c"])
    result = drain_last(s)
    assert result.step.command == "echo c"
    assert result.index == 2
    assert result.remaining == 2
    assert len(s.steps) == 2


def test_drain_last_empty_raises():
    s = make_session([])
    with pytest.raises(DrainError):
        drain_last(s)


def test_drain_at_middle():
    s = make_session(["a", "b", "c"])
    result = drain_at(s, 1)
    assert result.step.command == "b"
    assert result.index == 1
    assert result.remaining == 2
    assert [st.command for st in s.steps] == ["a", "c"]


def test_drain_at_out_of_range_raises():
    s = make_session(["a", "b"])
    with pytest.raises(DrainError, match="out of range"):
        drain_at(s, 5)


def test_drain_at_empty_raises():
    s = make_session([])
    with pytest.raises(DrainError):
        drain_at(s, 0)


def test_drain_all_returns_all_steps():
    s = make_session(["x", "y", "z"])
    results = drain_all(s)
    assert len(results) == 3
    assert [r.step.command for r in results] == ["x", "y", "z"]
    assert results[-1].remaining == 0
    assert len(s.steps) == 0


def test_drain_all_empty_raises():
    s = make_session([])
    with pytest.raises(DrainError):
        drain_all(s)


def test_drain_result_summary():
    s = make_session(["ls", "pwd"])
    result = drain_next(s)
    summary = result.summary()
    assert "1" in summary
    assert "remaining" in summary
