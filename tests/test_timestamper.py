"""Tests for breadcrumb.timestamper."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest

from breadcrumb.session import Session, Step
from breadcrumb.timestamper import (
    TimestamperError,
    apply_time_labels,
    clear_time_labels,
    get_time_label,
    META_KEY,
    FMT,
)


def make_session(commands=None, timestamps=None) -> Session:
    commands = commands or ["echo hello", "ls -la"]
    steps = []
    for i, cmd in enumerate(commands):
        ts = timestamps[i] if timestamps else datetime(2024, 6, 1, 10, i, 0).isoformat()
        steps.append(Step(command=cmd, timestamp=ts))
    return Session(id=str(uuid.uuid4()), name="test", steps=steps)


def test_apply_labels_sets_meta():
    session = make_session(["git status"])
    result = apply_time_labels(session)
    assert result.updated_count == 1
    assert META_KEY in session.steps[0].metadata


def test_apply_labels_format_matches_default():
    ts = datetime(2024, 6, 1, 10, 30, 0)
    session = make_session(["pwd"], [ts.isoformat()])
    apply_time_labels(session)
    label = session.steps[0].metadata[META_KEY]
    assert label == ts.strftime(FMT)


def test_apply_labels_skips_existing_without_overwrite():
    session = make_session(["echo a", "echo b"])
    session.steps[0].metadata[META_KEY] = "already set"
    result = apply_time_labels(session, overwrite=False)
    assert 0 in result.skipped_indices
    assert 1 in result.updated_indices
    assert session.steps[0].metadata[META_KEY] == "already set"


def test_apply_labels_overwrites_when_flag_set():
    session = make_session(["echo a"])
    session.steps[0].metadata[META_KEY] = "old label"
    result = apply_time_labels(session, overwrite=True)
    assert result.updated_count == 1
    assert session.steps[0].metadata[META_KEY] != "old label"


def test_apply_labels_empty_session_raises():
    session = Session(id=str(uuid.uuid4()), name="empty", steps=[])
    with pytest.raises(TimestamperError):
        apply_time_labels(session)


def test_apply_labels_invalid_timestamp_skipped():
    session = make_session(["bad"], ["not-a-date"])
    result = apply_time_labels(session)
    assert 0 in result.skipped_indices
    assert META_KEY not in session.steps[0].metadata


def test_clear_time_labels_removes_all():
    session = make_session(["a", "b"])
    apply_time_labels(session)
    removed = clear_time_labels(session)
    assert removed == 2
    for step in session.steps:
        assert META_KEY not in step.metadata


def test_clear_time_labels_returns_zero_when_none_set():
    session = make_session(["a", "b"])
    removed = clear_time_labels(session)
    assert removed == 0


def test_get_time_label_returns_value():
    session = make_session(["echo hi"])
    apply_time_labels(session)
    label = get_time_label(session, 0)
    assert label is not None
    assert isinstance(label, str)


def test_get_time_label_returns_none_when_not_set():
    session = make_session(["echo hi"])
    assert get_time_label(session, 0) is None


def test_get_time_label_out_of_range_raises():
    session = make_session(["echo hi"])
    with pytest.raises(TimestamperError):
        get_time_label(session, 99)


def test_summary_string():
    session = make_session(["a", "b", "c"])
    result = apply_time_labels(session)
    summary = result.summary()
    assert "3" in summary or "Updated" in summary
