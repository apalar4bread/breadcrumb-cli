"""Tests for breadcrumb/stamper.py."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from breadcrumb.session import Session, Step
from breadcrumb.stamper import (
    StampError,
    clear_stamp,
    get_stamp,
    is_stamped,
    list_stamped,
    stamp_step,
)


def make_session(commands: list[str] | None = None) -> Session:
    s = Session(name="test")
    for cmd in (commands or ["echo hello", "ls -la", "pwd"]):
        step = Step(command=cmd)
        s.steps.append(step)
    return s


def test_stamp_step_sets_metadata():
    session = make_session()
    step = stamp_step(session, 0)
    assert "stamped_at" in step.metadata


def test_stamp_step_timestamp_is_iso():
    session = make_session()
    step = stamp_step(session, 1)
    ts = step.metadata["stamped_at"]
    # Should parse without error
    datetime.fromisoformat(ts)


def test_stamp_step_with_label():
    session = make_session()
    step = stamp_step(session, 0, label="checkpoint")
    assert step.metadata.get("stamp_label") == "checkpoint"


def test_stamp_step_label_stripped():
    session = make_session()
    step = stamp_step(session, 0, label="  release  ")
    assert step.metadata["stamp_label"] == "release"


def test_stamp_step_no_label_removes_existing_label():
    session = make_session()
    stamp_step(session, 0, label="old")
    stamp_step(session, 0, label="")
    assert "stamp_label" not in session.steps[0].metadata


def test_stamp_step_custom_datetime():
    session = make_session()
    fixed = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    step = stamp_step(session, 0, at=fixed)
    assert step.metadata["stamped_at"] == fixed.isoformat()


def test_stamp_step_out_of_range_raises():
    session = make_session()
    with pytest.raises(StampError):
        stamp_step(session, 99)


def test_stamp_step_negative_index_raises():
    session = make_session()
    with pytest.raises(StampError):
        stamp_step(session, -1)


def test_clear_stamp_removes_metadata():
    session = make_session()
    stamp_step(session, 0, label="x")
    clear_stamp(session, 0)
    assert not is_stamped(session.steps[0])
    assert "stamp_label" not in session.steps[0].metadata


def test_clear_stamp_out_of_range_raises():
    session = make_session()
    with pytest.raises(StampError):
        clear_stamp(session, 10)


def test_is_stamped_false_by_default():
    session = make_session()
    assert not is_stamped(session.steps[0])


def test_is_stamped_true_after_stamp():
    session = make_session()
    stamp_step(session, 2)
    assert is_stamped(session.steps[2])


def test_get_stamp_returns_none_if_not_stamped():
    session = make_session()
    assert get_stamp(session.steps[0]) is None


def test_list_stamped_returns_correct_indices():
    session = make_session()
    stamp_step(session, 0)
    stamp_step(session, 2)
    result = list_stamped(session)
    assert [i for i, _ in result] == [0, 2]


def test_list_stamped_empty_when_none():
    session = make_session()
    assert list_stamped(session) == []
