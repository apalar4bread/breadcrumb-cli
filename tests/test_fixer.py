"""Tests for breadcrumb.fixer."""

import pytest

from breadcrumb.session import Session, Step
from breadcrumb.fixer import fix_session, FixError


def make_session(*commands, notes=None) -> Session:
    notes = notes or []
    steps = []
    for i, cmd in enumerate(commands):
        note = notes[i] if i < len(notes) else ""
        steps.append(Step(command=cmd, note=note))
    return Session(id="s1", name="test", steps=steps)


def test_fix_no_issues_returns_no_fixes():
    s = make_session("ls", "pwd")
    result = fix_session(s)
    assert result.fix_count == 0
    assert "No fixes" in result.summary()


def test_fix_removes_empty_commands():
    s = make_session("ls", "", "pwd")
    result = fix_session(s, remove_empty=True)
    assert len(result.session.steps) == 2
    assert result.fix_count == 1


def test_fix_strips_command_whitespace():
    s = make_session("  ls  ", "pwd")
    result = fix_session(s, strip_whitespace=True)
    assert result.session.steps[0].command == "ls"
    assert result.fix_count == 1


def test_fix_strips_note_whitespace():
    s = make_session("ls", notes=["  list files  "])
    result = fix_session(s, strip_whitespace=True)
    assert result.session.steps[0].note == "list files"
    assert result.fix_count == 1


def test_fix_deduplicates_notes():
    s = make_session("ls", "pwd", notes=["same note", "same note"])
    result = fix_session(s, dedupe_notes=True)
    assert result.session.steps[1].note == ""
    assert result.fix_count == 1


def test_fix_dedupe_notes_case_insensitive():
    s = make_session("ls", "pwd", notes=["Note", "note"])
    result = fix_session(s, dedupe_notes=True)
    assert result.session.steps[1].note == ""


def test_fix_multiple_issues():
    s = make_session("  ls  ", "", "pwd", notes=["  note  ", "", ""])
    result = fix_session(s)
    assert result.fix_count >= 2


def test_fix_no_id_raises():
    s = Session(id="", name="test", steps=[Step(command="ls")])
    with pytest.raises(FixError):
        fix_session(s)


def test_fix_summary_lists_fixes():
    s = make_session("  ls  ")
    result = fix_session(s)
    summary = result.summary()
    assert "fix" in summary.lower()
    assert "strip" in summary.lower()


def test_fix_preserve_unaffected_steps():
    s = make_session("ls", "pwd", "echo hi")
    result = fix_session(s)
    cmds = [step.command for step in result.session.steps]
    assert cmds == ["ls", "pwd", "echo hi"]
