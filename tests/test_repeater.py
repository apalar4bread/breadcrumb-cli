"""Tests for breadcrumb.repeater."""

import pytest
from breadcrumb.session import Session, Step
from breadcrumb.repeater import (
    RepeatError,
    mark_repeat,
    clear_repeat,
    expand_repeats,
)


def make_session(commands=None):
    steps = [
        Step(command=cmd, note="", metadata={}, timestamp="2024-01-01T00:00:00")
        for cmd in (commands or ["echo a", "echo b", "echo c"])
    ]
    return Session(
        id="test-id",
        name="test",
        created_at="2024-01-01T00:00:00",
        steps=steps,
        tags=[],
        metadata={},
    )


def test_mark_repeat_sets_metadata():
    s = make_session()
    mark_repeat(s, 0, times=3)
    assert s.steps[0].metadata["repeat"] == "3"


def test_mark_repeat_does_not_affect_others():
    s = make_session()
    mark_repeat(s, 1, times=2)
    assert "repeat" not in s.steps[0].metadata
    assert "repeat" not in s.steps[2].metadata


def test_mark_repeat_invalid_times_raises():
    s = make_session()
    with pytest.raises(RepeatError, match="times must be"):
        mark_repeat(s, 0, times=1)


def test_mark_repeat_out_of_range_raises():
    s = make_session()
    with pytest.raises(RepeatError, match="out of range"):
        mark_repeat(s, 99, times=2)


def test_clear_repeat_removes_flag():
    s = make_session()
    mark_repeat(s, 0, times=2)
    clear_repeat(s, 0)
    assert "repeat" not in s.steps[0].metadata


def test_clear_repeat_no_error_if_not_set():
    s = make_session()
    clear_repeat(s, 0)  # should not raise


def test_expand_repeats_no_markers_returns_same_count():
    s = make_session(["ls", "pwd"])
    result = expand_repeats(s)
    assert len(result.new_session.steps) == 2
    assert result.repeated_count == 0


def test_expand_repeats_doubles_marked_step():
    s = make_session(["ls", "pwd"])
    mark_repeat(s, 0, times=2)
    result = expand_repeats(s)
    assert len(result.new_session.steps) == 3
    assert result.repeated_count == 1


def test_expand_repeats_triples_marked_step():
    s = make_session(["ls"])
    mark_repeat(s, 0, times=3)
    result = expand_repeats(s)
    assert len(result.new_session.steps) == 3
    assert result.repeated_count == 2


def test_expand_repeats_copies_are_tagged():
    s = make_session(["ls"])
    mark_repeat(s, 0, times=2)
    result = expand_repeats(s)
    copy_step = result.new_session.steps[1]
    assert copy_step.metadata.get("repeat_copy") == "true"


def test_expand_repeats_custom_name():
    s = make_session()
    result = expand_repeats(s, name="my expanded")
    assert result.new_session.name == "my expanded"


def test_expand_repeats_default_name_contains_original():
    s = make_session()
    result = expand_repeats(s)
    assert "test" in result.new_session.name


def test_expand_repeats_empty_session_raises():
    s = make_session([])
    with pytest.raises(RepeatError, match="empty"):
        expand_repeats(s)


def test_expand_repeats_summary_string():
    s = make_session(["ls"])
    mark_repeat(s, 0, times=2)
    result = expand_repeats(s)
    assert "Repeated" in result.summary
