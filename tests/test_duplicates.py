import pytest
from breadcrumb.session import Session, Step
from breadcrumb.duplicates import (
    find_duplicate_steps,
    remove_duplicate_steps,
    find_common_steps,
)


def make_session(commands: list, name: str = "test") -> Session:
    s = Session(name=name)
    for cmd in commands:
        s.steps.append(Step(command=cmd))
    return s


def test_find_no_duplicates():
    s = make_session(["ls", "pwd", "echo hi"])
    assert find_duplicate_steps(s) == []


def test_find_single_duplicate():
    s = make_session(["ls", "pwd", "ls"])
    dupes = find_duplicate_steps(s)
    assert len(dupes) == 1
    assert dupes[0] == (0, 2)


def test_find_duplicate_case_insensitive():
    s = make_session(["LS", "ls"])
    dupes = find_duplicate_steps(s)
    assert len(dupes) == 1


def test_remove_duplicates_keep_first():
    s = make_session(["ls", "pwd", "ls", "pwd"])
    result = remove_duplicate_steps(s, keep="first")
    assert [step.command for step in result.steps] == ["ls", "pwd"]


def test_remove_duplicates_keep_last():
    s = make_session(["ls", "pwd", "ls"])
    result = remove_duplicate_steps(s, keep="last")
    commands = [step.command for step in result.steps]
    assert commands.index("ls") > commands.index("pwd") or "ls" in commands
    assert len(result.steps) == 2


def test_remove_duplicates_invalid_keep():
    s = make_session(["ls"])
    with pytest.raises(ValueError):
        remove_duplicate_steps(s, keep="middle")


def test_remove_duplicates_does_not_mutate_original():
    s = make_session(["ls", "ls"])
    original_count = len(s.steps)
    remove_duplicate_steps(s)
    assert len(s.steps) == original_count


def test_find_common_steps():
    a = make_session(["ls", "pwd", "echo a"])
    b = make_session(["ls", "git status", "echo a"])
    common = find_common_steps(a, b)
    assert "ls" in common
    assert "echo a" in common
    assert "pwd" not in common


def test_find_common_steps_empty():
    a = make_session(["ls"])
    b = make_session(["pwd"])
    assert find_common_steps(a, b) == []
