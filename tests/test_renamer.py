"""Tests for breadcrumb.renamer."""

import pytest
from breadcrumb.session import Session, Step
from breadcrumb.renamer import rename_session, rename_step_note, rename_step_command, RenameError


def make_session():
    s = Session(id="s1", name="original", steps=[])
    s.steps.append(Step(command="echo hello", metadata={"note": "first step"}))
    s.steps.append(Step(command="ls -la", metadata={}))
    return s


def test_rename_session_basic():
    s = make_session()
    rename_session(s, "new name")
    assert s.name == "new name"


def test_rename_session_strips_whitespace():
    s = make_session()
    rename_session(s, "  trimmed  ")
    assert s.name == "trimmed"


def test_rename_session_blank_raises():
    s = make_session()
    with pytest.raises(RenameError, match="blank"):
        rename_session(s, "   ")


def test_rename_session_too_long_raises():
    s = make_session()
    with pytest.raises(RenameError, match="too long"):
        rename_session(s, "x" * 129)


def test_rename_session_updates_updated_at():
    s = make_session()
    old_ts = getattr(s, "updated_at", None)
    rename_session(s, "fresh name")
    assert s.updated_at != old_ts


def test_rename_step_note():
    s = make_session()
    rename_step_note(s, 0, "updated note")
    assert s.steps[0].metadata["note"] == "updated note"


def test_rename_step_note_out_of_range():
    s = make_session()
    with pytest.raises(RenameError, match="out of range"):
        rename_step_note(s, 5, "nope")


def test_rename_step_command_basic():
    s = make_session()
    rename_step_command(s, 1, "pwd")
    assert s.steps[1].command == "pwd"


def test_rename_step_command_blank_raises():
    s = make_session()
    with pytest.raises(RenameError, match="blank"):
        rename_step_command(s, 0, "  ")


def test_rename_step_command_negative_index_raises():
    s = make_session()
    with pytest.raises(RenameError, match="out of range"):
        rename_step_command(s, -1, "echo hi")
