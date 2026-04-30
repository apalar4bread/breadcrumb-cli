"""Tests for breadcrumb.squasher."""
import pytest

from breadcrumb.session import Session, Step
from breadcrumb.squasher import SquashError, SquashResult, squash_session


def make_session(commands, notes=None):
    notes = notes or [None] * len(commands)
    s = Session(name="test")
    for cmd, note in zip(commands, notes):
        s.steps.append(Step(command=cmd, note=note))
    return s


def test_squash_empty_raises():
    s = Session(name="empty")
    with pytest.raises(SquashError):
        squash_session(s)


def test_squash_no_consecutive_duplicates():
    s = make_session(["ls", "pwd", "echo hi"])
    result = squash_session(s)
    assert result.original_count == 3
    assert result.squashed_count == 3
    assert result.groups_merged == 0


def test_squash_single_consecutive_pair():
    s = make_session(["ls", "ls", "pwd"])
    result = squash_session(s)
    assert result.squashed_count == 2
    assert result.groups_merged == 1
    assert s.steps[0].command == "ls"
    assert s.steps[1].command == "pwd"


def test_squash_entire_session_same_command():
    s = make_session(["make", "make", "make", "make"])
    result = squash_session(s)
    assert result.squashed_count == 1
    assert result.groups_merged == 1
    assert result.original_count == 4


def test_squash_non_adjacent_duplicates_kept():
    s = make_session(["ls", "pwd", "ls"])
    result = squash_session(s)
    assert result.squashed_count == 3
    assert result.groups_merged == 0


def test_squash_case_insensitive_by_default():
    s = make_session(["LS", "ls", "pwd"])
    result = squash_session(s)
    assert result.squashed_count == 2
    assert result.groups_merged == 1


def test_squash_case_sensitive_keeps_both():
    s = make_session(["LS", "ls", "pwd"])
    result = squash_session(s, case_sensitive=True)
    assert result.squashed_count == 3
    assert result.groups_merged == 0


def test_squash_combines_notes_by_default():
    s = make_session(["git push", "git push"], notes=["first try", "second try"])
    squash_session(s)
    assert "first try" in s.steps[0].note
    assert "second try" in s.steps[0].note


def test_squash_combine_notes_false_keeps_first_note():
    s = make_session(["git push", "git push"], notes=["first try", "second try"])
    squash_session(s, combine_notes=False)
    assert s.steps[0].note == "first try"


def test_squash_duplicate_notes_not_repeated():
    s = make_session(["echo", "echo"], notes=["hi", "hi"])
    squash_session(s)
    # "hi" should not appear twice
    assert s.steps[0].note.count("hi") == 1


def test_squash_result_summary_string():
    s = make_session(["ls", "ls", "pwd"])
    result = squash_session(s)
    summary = result.summary
    assert "3" in summary
    assert "2" in summary


def test_squash_preserves_metadata():
    s = make_session(["docker build", "docker build"])
    s.steps[0].metadata["pinned"] = True
    result = squash_session(s)
    assert result.session.steps[0].metadata.get("pinned") is True
