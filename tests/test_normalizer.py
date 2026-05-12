"""Tests for breadcrumb.normalizer."""

import pytest
from breadcrumb.session import Session, Step
from breadcrumb.normalizer import normalize_session, NormalizeResult


def make_session(commands, notes=None):
    session = Session(name="test")
    notes = notes or [""] * len(commands)
    for cmd, note in zip(commands, notes):
        step = Step(command=cmd, note=note)
        session.steps.append(step)
    return session


def test_normalize_clean_session_no_changes():
    s = make_session(["git status", "ls -la"])
    result = normalize_session(s)
    assert result.change_count == 0
    assert result.summary() == "No changes made."


def test_normalize_command_strips_whitespace():
    s = make_session(["  git   status  "])
    result = normalize_session(s)
    assert s.steps[0].command == "git status"
    assert result.change_count == 1


def test_normalize_command_collapses_internal_spaces():
    s = make_session(["ls   -la   /tmp"])
    result = normalize_session(s)
    assert s.steps[0].command == "ls -la /tmp"
    assert result.change_count == 1


def test_normalize_note_strips_whitespace():
    s = make_session(["echo hi"], notes=["  my note  "])
    result = normalize_session(s)
    assert s.steps[0].note == "my note"
    assert result.change_count == 1


def test_normalize_empty_note_not_changed():
    s = make_session(["echo hi"], notes=[""])
    result = normalize_session(s)
    assert result.change_count == 0


def test_normalize_commands_only_flag():
    s = make_session(["  ls  "], notes=["  note  "])
    result = normalize_session(s, commands=True, notes=False)
    assert s.steps[0].command == "ls"
    assert s.steps[0].note == "  note  "
    assert result.change_count == 1


def test_normalize_notes_only_flag():
    s = make_session(["  ls  "], notes=["  note  "])
    result = normalize_session(s, commands=False, notes=True)
    assert s.steps[0].command == "  ls  "
    assert s.steps[0].note == "note"
    assert result.change_count == 1


def test_normalize_empty_session_returns_no_changes():
    s = Session(name="empty")
    result = normalize_session(s)
    assert result.change_count == 0
    assert result.session is s


def test_normalize_summary_with_changes():
    s = make_session(["  ls  ", "  pwd  "])
    result = normalize_session(s)
    assert "2 change(s)" in result.summary()


def test_normalize_multiple_steps_multiple_changes():
    s = make_session(
        ["  git  log  ", "docker  ps"],
        notes=["  a note  ", "clean"]
    )
    result = normalize_session(s)
    assert s.steps[0].command == "git log"
    assert s.steps[1].command == "docker ps"
    assert s.steps[0].note == "a note"
    assert result.change_count == 2
