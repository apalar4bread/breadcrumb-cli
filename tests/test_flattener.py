"""Tests for breadcrumb.flattener."""

import pytest
from breadcrumb.session import Session, Step
from breadcrumb.flattener import (
    FlattenError,
    FlattenResult,
    flatten_sessions,
    flatten_to_session,
    format_flatten_result,
)


def make_session(name: str, commands) -> Session:
    s = Session(name=name)
    for cmd in commands:
        if isinstance(cmd, tuple):
            s.steps.append(Step(command=cmd[0], note=cmd[1]))
        else:
            s.steps.append(Step(command=cmd))
    return s


def test_flatten_empty_raises():
    with pytest.raises(FlattenError):
        flatten_sessions([])


def test_flatten_single_session():
    s = make_session("alpha", ["ls", "pwd"])
    result = flatten_sessions([s])
    assert result.source_count == 1
    assert result.total_steps == 2
    assert result.steps[0] == ("alpha", s.steps[0])
    assert result.steps[1] == ("alpha", s.steps[1])


def test_flatten_multiple_sessions_order():
    s1 = make_session("a", ["echo a", "echo b"])
    s2 = make_session("b", ["echo c"])
    result = flatten_sessions([s1, s2])
    assert result.total_steps == 3
    assert result.steps[0][0] == "a"
    assert result.steps[1][0] == "a"
    assert result.steps[2][0] == "b"


def test_flatten_preserves_commands():
    s1 = make_session("x", ["git status"])
    s2 = make_session("y", ["git log"])
    result = flatten_sessions([s1, s2])
    commands = [step.command for _, step in result.steps]
    assert commands == ["git status", "git log"]


def test_flatten_to_session_empty_raises():
    with pytest.raises(FlattenError):
        flatten_to_session([])


def test_flatten_to_session_custom_name():
    s = make_session("alpha", ["ls"])
    new = flatten_to_session([s], name="my-flat")
    assert new.name == "my-flat"


def test_flatten_to_session_default_name():
    s1 = make_session("alpha", ["ls"])
    s2 = make_session("beta", ["pwd"])
    new = flatten_to_session([s1, s2])
    assert "alpha" in new.name
    assert "beta" in new.name


def test_flatten_to_session_steps_are_independent():
    s = make_session("src", ["echo hi"])
    new = flatten_to_session([s])
    new.steps[0].command = "changed"
    assert s.steps[0].command == "echo hi"


def test_flatten_to_session_step_count():
    s1 = make_session("a", ["a1", "a2"])
    s2 = make_session("b", ["b1"])
    new = flatten_to_session([s1, s2])
    assert len(new.steps) == 3


def test_format_flatten_result_contains_session_name():
    s = make_session("myses", [("git pull", "fetch latest")])
    result = flatten_sessions([s])
    output = format_flatten_result(result)
    assert "myses" in output
    assert "git pull" in output
    assert "fetch latest" in output


def test_format_flatten_result_summary_line():
    s1 = make_session("a", ["x"])
    s2 = make_session("b", ["y", "z"])
    result = flatten_sessions([s1, s2])
    output = format_flatten_result(result)
    assert "2 session" in output
    assert "3 step" in output
