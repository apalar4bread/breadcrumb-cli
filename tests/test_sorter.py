"""Tests for breadcrumb.sorter."""

import pytest
from breadcrumb.session import Session, Step
from breadcrumb.sorter import sort_steps, sort_by_command, sort_by_note, SortError


def make_session(commands):
    steps = [
        Step(command=cmd, note=f"note-{cmd}", timestamp=f"2024-01-0{i+1}T00:00:00")
        for i, cmd in enumerate(commands)
    ]
    return Session(id="s1", name="test", steps=steps)


def test_sort_by_timestamp_ascending():
    session = make_session(["c", "a", "b"])
    # manually scramble timestamps
    session.steps[0].timestamp = "2024-01-03T00:00:00"
    session.steps[1].timestamp = "2024-01-01T00:00:00"
    session.steps[2].timestamp = "2024-01-02T00:00:00"
    result = sort_steps(session, key="timestamp")
    assert [s.timestamp for s in result.steps] == [
        "2024-01-01T00:00:00",
        "2024-01-02T00:00:00",
        "2024-01-03T00:00:00",
    ]


def test_sort_by_command_ascending():
    session = make_session(["zebra", "apple", "mango"])
    result = sort_by_command(session)
    assert [s.command for s in result.steps] == ["apple", "mango", "zebra"]


def test_sort_by_command_descending():
    session = make_session(["zebra", "apple", "mango"])
    result = sort_by_command(session, reverse=True)
    assert [s.command for s in result.steps] == ["zebra", "mango", "apple"]


def test_sort_by_note():
    session = make_session(["a", "b", "c"])
    session.steps[0].note = "zzz"
    session.steps[1].note = "aaa"
    session.steps[2].note = "mmm"
    result = sort_by_note(session)
    assert [s.note for s in result.steps] == ["aaa", "mmm", "zzz"]


def test_sort_does_not_mutate_original():
    session = make_session(["z", "a"])
    original_order = [s.command for s in session.steps]
    sort_by_command(session)
    assert [s.command for s in session.steps] == original_order


def test_sort_invalid_key_raises():
    session = make_session(["a"])
    with pytest.raises(SortError, match="Invalid sort key"):
        sort_steps(session, key="nonexistent")


def test_sort_preserves_session_metadata():
    session = make_session(["b", "a"])
    session.tags = ["mytag"]
    result = sort_by_command(session)
    assert result.id == session.id
    assert result.name == session.name
    assert result.tags == ["mytag"]
