"""Tests for breadcrumb.counter."""
import pytest

from breadcrumb.session import Session, Step
from breadcrumb.counter import (
    CounterError,
    count_by_command,
    count_by_note,
    count_by_metadata_key,
    count_all,
)


def make_session(*commands) -> Session:
    s = Session(id="s1", name="test")
    for cmd in commands:
        s.steps.append(Step(command=cmd))
    return s


# --- count_all ---

def test_count_all_empty():
    s = make_session()
    assert count_all(s) == 0


def test_count_all_several():
    s = make_session("ls", "pwd", "echo hi")
    assert count_all(s) == 3


# --- count_by_command ---

def test_count_by_command_found():
    s = make_session("git status", "git commit", "ls")
    result = count_by_command(s, "git")
    assert result.matched == 2
    assert result.total == 3


def test_count_by_command_none_found():
    s = make_session("ls", "pwd")
    result = count_by_command(s, "docker")
    assert result.matched == 0


def test_count_by_command_case_insensitive_default():
    s = make_session("GIT status", "git commit")
    result = count_by_command(s, "git")
    assert result.matched == 2


def test_count_by_command_case_sensitive_no_match():
    s = make_session("GIT status")
    result = count_by_command(s, "git", case_sensitive=True)
    assert result.matched == 0


def test_count_by_command_empty_pattern_raises():
    s = make_session("ls")
    with pytest.raises(CounterError):
        count_by_command(s, "")


def test_count_by_command_summary_string():
    s = make_session("ls", "ls -la")
    result = count_by_command(s, "ls")
    assert "ls" in result.summary
    assert "2/2" in result.summary


# --- count_by_note ---

def test_count_by_note_found():
    s = make_session("ls", "pwd")
    s.steps[0].note = "list files"
    s.steps[1].note = "print working dir"
    result = count_by_note(s, "list")
    assert result.matched == 1


def test_count_by_note_none_found():
    s = make_session("ls")
    s.steps[0].note = "list files"
    result = count_by_note(s, "docker")
    assert result.matched == 0


def test_count_by_note_empty_pattern_raises():
    s = make_session("ls")
    with pytest.raises(CounterError):
        count_by_note(s, "")


def test_count_by_note_skips_none_notes():
    s = make_session("ls", "pwd")
    # steps have no note set (None)
    result = count_by_note(s, "anything")
    assert result.matched == 0


# --- count_by_metadata_key ---

def test_count_by_metadata_key_found():
    s = make_session("ls", "pwd", "echo")
    s.steps[0].metadata["pinned"] = True
    s.steps[2].metadata["pinned"] = True
    result = count_by_metadata_key(s, "pinned")
    assert result.matched == 2


def test_count_by_metadata_key_none():
    s = make_session("ls", "pwd")
    result = count_by_metadata_key(s, "pinned")
    assert result.matched == 0


def test_count_by_metadata_key_empty_raises():
    s = make_session("ls")
    with pytest.raises(CounterError):
        count_by_metadata_key(s, "")
