"""Tests for breadcrumb/truncator.py."""

import pytest
from breadcrumb.session import Session, Step
from breadcrumb.truncator import (
    TruncateError,
    TruncateResult,
    truncate_session,
    DEFAULT_MAX_LENGTH,
)


def make_session(commands, notes=None):
    session = Session(name="test")
    notes = notes or [None] * len(commands)
    for cmd, note in zip(commands, notes):
        step = Step(command=cmd, note=note)
        session.steps.append(step)
    return session


def test_truncate_no_changes_when_short():
    s = make_session(["ls", "pwd"])
    result = truncate_session(s, max_length=20)
    assert result.truncated_count == 0
    assert result.affected_indices == []
    assert s.steps[0].command == "ls"


def test_truncate_command_too_long():
    long_cmd = "a" * 100
    s = make_session([long_cmd])
    result = truncate_session(s, max_length=10)
    assert result.truncated_count == 1
    assert 0 in result.affected_indices
    assert len(s.steps[0].command) == 10
    assert s.steps[0].command.endswith("...")


def test_truncate_note_too_long():
    long_note = "n" * 200
    s = make_session(["echo hi"], notes=[long_note])
    result = truncate_session(s, max_length=20)
    assert result.truncated_count == 1
    assert s.steps[0].note.endswith("...")
    assert len(s.steps[0].note) == 20


def test_truncate_command_only():
    long_note = "n" * 200
    long_cmd = "c" * 200
    s = make_session([long_cmd], notes=[long_note])
    result = truncate_session(s, max_length=30, truncate_commands=True, truncate_notes=False)
    assert len(s.steps[0].command) == 30
    assert len(s.steps[0].note) == 200  # untouched


def test_truncate_note_only():
    long_note = "n" * 200
    long_cmd = "c" * 200
    s = make_session([long_cmd], notes=[long_note])
    result = truncate_session(s, max_length=30, truncate_commands=False, truncate_notes=True)
    assert len(s.steps[0].command) == 200  # untouched
    assert len(s.steps[0].note) == 30


def test_truncate_none_note_ignored():
    s = make_session(["ls"], notes=[None])
    result = truncate_session(s, max_length=5)
    assert result.truncated_count == 0


def test_truncate_multiple_steps_mixed():
    s = make_session(["a" * 100, "short", "b" * 100])
    result = truncate_session(s, max_length=20)
    assert result.truncated_count == 2
    assert 0 in result.affected_indices
    assert 1 not in result.affected_indices
    assert 2 in result.affected_indices


def test_truncate_custom_suffix():
    s = make_session(["x" * 50])
    result = truncate_session(s, max_length=10, suffix=">>")
    assert s.steps[0].command.endswith(">>")
    assert len(s.steps[0].command) == 10


def test_truncate_invalid_max_length_raises():
    s = make_session(["ls"])
    with pytest.raises(TruncateError):
        truncate_session(s, max_length=0)


def test_truncate_both_false_raises():
    s = make_session(["ls"])
    with pytest.raises(TruncateError):
        truncate_session(s, truncate_commands=False, truncate_notes=False)


def test_summary_no_truncation():
    s = make_session(["ls"])
    result = truncate_session(s, max_length=100)
    assert "No steps" in result.summary()


def test_summary_with_truncation():
    s = make_session(["a" * 100])
    result = truncate_session(s, max_length=10)
    assert "Truncated" in result.summary()
    assert "0" in result.summary()
