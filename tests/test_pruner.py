"""Tests for breadcrumb.pruner."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from breadcrumb.pruner import (
    PruneError,
    prune_beyond_count,
    prune_empty_commands,
    prune_older_than,
)
from breadcrumb.session import Session, Step


def _ts(days_ago: int = 0) -> str:
    dt = datetime.now(tz=timezone.utc) - timedelta(days=days_ago)
    return dt.isoformat()


def make_session(commands: list[str], ages_days: list[int] | None = None) -> Session:
    s = Session(name="test")
    for i, cmd in enumerate(commands):
        age = ages_days[i] if ages_days else 0
        s.steps.append(Step(command=cmd, timestamp=_ts(age)))
    return s


# --- prune_older_than ---

def test_prune_older_than_removes_old_steps():
    s = make_session(["old", "new"], ages_days=[10, 1])
    result = prune_older_than(s, days=5)
    assert result.removed_count == 1
    assert result.removed[0].command == "old"
    assert len(s.steps) == 1
    assert s.steps[0].command == "new"


def test_prune_older_than_keeps_all_when_within_threshold():
    s = make_session(["a", "b"], ages_days=[2, 3])
    result = prune_older_than(s, days=5)
    assert result.removed_count == 0
    assert result.kept_count == 2


def test_prune_older_than_removes_all():
    s = make_session(["x", "y"], ages_days=[20, 30])
    result = prune_older_than(s, days=5)
    assert result.removed_count == 2
    assert len(s.steps) == 0


def test_prune_older_than_negative_days_raises():
    s = make_session(["cmd"])
    with pytest.raises(PruneError):
        prune_older_than(s, days=-1)


def test_prune_older_than_zero_days_removes_older_than_today():
    s = make_session(["recent", "old"], ages_days=[0, 1])
    result = prune_older_than(s, days=0)
    # age_days > 0 => old step removed
    assert result.removed_count == 1
    assert result.removed[0].command == "old"


# --- prune_beyond_count ---

def test_prune_beyond_count_keeps_most_recent():
    s = make_session(["a", "b", "c", "d"])
    result = prune_beyond_count(s, max_steps=2)
    assert result.removed_count == 2
    assert [st.command for st in s.steps] == ["c", "d"]


def test_prune_beyond_count_no_op_when_under_limit():
    s = make_session(["a", "b"])
    result = prune_beyond_count(s, max_steps=5)
    assert result.removed_count == 0
    assert result.kept_count == 2


def test_prune_beyond_count_zero_removes_all():
    s = make_session(["a", "b", "c"])
    result = prune_beyond_count(s, max_steps=0)
    assert result.removed_count == 3
    assert len(s.steps) == 0


def test_prune_beyond_count_negative_raises():
    s = make_session(["cmd"])
    with pytest.raises(PruneError):
        prune_beyond_count(s, max_steps=-1)


# --- prune_empty_commands ---

def test_prune_empty_commands_removes_blank():
    s = make_session(["ls", "", "  ", "pwd"])
    result = prune_empty_commands(s)
    assert result.removed_count == 2
    assert [st.command for st in s.steps] == ["ls", "pwd"]


def test_prune_empty_commands_no_blanks():
    s = make_session(["git status", "echo hi"])
    result = prune_empty_commands(s)
    assert result.removed_count == 0
    assert result.kept_count == 2


def test_prune_result_summary_message():
    s = make_session(["a", "b", "c", "d"])
    result = prune_beyond_count(s, max_steps=2)
    assert "2" in result.summary()
    assert "kept" in result.summary()
