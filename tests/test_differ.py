import pytest
from breadcrumb.session import Session, Step
from breadcrumb.differ import diff_sessions, format_diff, sessions_are_identical


def make_session(name: str, commands: list) -> Session:
    s = Session(name=name)
    for cmd in commands:
        s.steps.append(Step(command=cmd))
    return s


def test_identical_sessions():
    a = make_session("a", ["echo hi", "ls"])
    b = make_session("b", ["echo hi", "ls"])
    diffs = diff_sessions(a, b)
    assert sessions_are_identical(diffs)
    assert len(diffs) == 2


def test_added_step():
    a = make_session("a", ["echo hi"])
    b = make_session("b", ["echo hi", "ls"])
    diffs = diff_sessions(a, b)
    assert diffs[1]["status"] == "added"
    assert diffs[1]["step"].command == "ls"


def test_removed_step():
    a = make_session("a", ["echo hi", "ls"])
    b = make_session("b", ["echo hi"])
    diffs = diff_sessions(a, b)
    assert diffs[1]["status"] == "removed"
    assert diffs[1]["step"].command == "ls"


def test_changed_step():
    a = make_session("a", ["echo hi"])
    b = make_session("b", ["echo bye"])
    diffs = diff_sessions(a, b)
    assert diffs[0]["status"] == "changed"
    assert diffs[0]["old"].command == "echo hi"
    assert diffs[0]["new"].command == "echo bye"


def test_format_diff_output():
    a = make_session("a", ["echo hi", "rm file"])
    b = make_session("b", ["echo hi", "ls"])
    diffs = diff_sessions(a, b)
    output = format_diff(diffs)
    assert "  [0] echo hi" in output
    assert "- [1] rm file" in output
    assert "+ [1] ls" in output


def test_empty_sessions():
    a = make_session("a", [])
    b = make_session("b", [])
    diffs = diff_sessions(a, b)
    assert diffs == []
    assert sessions_are_identical(diffs)


def test_sessions_not_identical_when_changed():
    a = make_session("a", ["echo hi"])
    b = make_session("b", ["echo bye"])
    diffs = diff_sessions(a, b)
    assert not sessions_are_identical(diffs)
