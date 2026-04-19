"""Tests for breadcrumb.narrator."""

import pytest
from breadcrumb.session import Session, Step
from breadcrumb.narrator import narrate_session, format_narration, NarratorError


def make_session(steps=None):
    s = Session(id="s1", name="test-session")
    for step in (steps or []):
        s.steps.append(step)
    return s


def make_step(command, note="", **meta):
    return Step(command=command, note=note, metadata=meta if meta else {})


def test_narrate_empty_session_raises():
    s = make_session()
    with pytest.raises(NarratorError):
        narrate_session(s)


def test_narrate_basic_step():
    s = make_session([make_step("ls -la")])
    lines = narrate_session(s)
    assert len(lines) == 1
    assert "Step 1" in lines[0].text
    assert "ls -la" in lines[0].text


def test_narrate_step_with_note():
    s = make_session([make_step("git status", note="check repo state")])
    lines = narrate_session(s)
    assert "check repo state" in lines[0].text


def test_narrate_step_pinned():
    s = make_session([make_step("echo hi", pinned=True)])
    lines = narrate_session(s)
    assert "[pinned]" in lines[0].text


def test_narrate_step_bookmarked():
    s = make_session([make_step("pwd", bookmarked=True)])
    lines = narrate_session(s)
    assert "[bookmarked]" in lines[0].text


def test_narrate_step_annotation():
    s = make_session([make_step("make build", annotation="builds the project")])
    lines = narrate_session(s)
    assert "builds the project" in lines[0].text


def test_narrate_step_label():
    s = make_session([make_step("pytest", label="test")])
    lines = narrate_session(s)
    assert "label:test" in lines[0].text


def test_narrate_multiple_steps_index():
    steps = [make_step("cmd1"), make_step("cmd2"), make_step("cmd3")]
    s = make_session(steps)
    lines = narrate_session(s)
    assert lines[0].index == 0
    assert lines[2].index == 2
    assert "Step 3" in lines[2].text


def test_format_narration_with_title():
    s = make_session([make_step("echo hello")])
    lines = narrate_session(s)
    output = format_narration(lines, title="My Session")
    assert output.startswith("# My Session")
    assert "echo hello" in output


def test_format_narration_no_title():
    s = make_session([make_step("echo hello")])
    lines = narrate_session(s)
    output = format_narration(lines)
    assert not output.startswith("#")
    assert "echo hello" in output
