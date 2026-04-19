import pytest
from breadcrumb.session import Session, Step
from breadcrumb.grouper import group_steps, group_by_command, group_by_note, group_by_label, group_by_tag, GroupError


def make_session(*steps):
    s = Session(name="test")
    s.steps = list(steps)
    return s


def make_step(command, note="", metadata=None):
    return Step(command=command, note=note, metadata=metadata or {})


def test_group_by_command_basic():
    s = make_session(make_step("git status"), make_step("git push"), make_step("ls -la"))
    groups = group_by_command(s)
    assert "git" in groups
    assert len(groups["git"]) == 2
    assert "ls" in groups


def test_group_by_command_empty_command():
    s = make_session(make_step(""), make_step("echo hi"))
    groups = group_by_command(s)
    assert "(empty)" in groups


def test_group_by_note_groups_correctly():
    s = make_session(make_step("a", note="setup"), make_step("b", note="setup"), make_step("c", note="cleanup"))
    groups = group_by_note(s)
    assert len(groups["setup"]) == 2
    assert len(groups["cleanup"]) == 1


def test_group_by_note_no_note():
    s = make_session(make_step("ls"), make_step("pwd"))
    groups = group_by_note(s)
    assert "(no note)" in groups
    assert len(groups["(no note)"]) == 2


def test_group_by_label():
    s = make_session(
        make_step("a", metadata={"label": "infra"}),
        make_step("b", metadata={"label": "infra"}),
        make_step("c"),
    )
    groups = group_by_label(s)
    assert len(groups["infra"]) == 2
    assert "(unlabeled)" in groups


def test_group_by_tag_multiple_tags():
    s = make_session(
        make_step("a", metadata={"tags": ["ci", "docker"]}),
        make_step("b", metadata={"tags": ["ci"]}),
        make_step("c"),
    )
    groups = group_by_tag(s)
    assert len(groups["ci"]) == 2
    assert len(groups["docker"]) == 1
    assert "(untagged)" in groups


def test_group_steps_invalid_key():
    s = make_session(make_step("ls"))
    with pytest.raises(GroupError):
        group_steps(s, "invalid")


def test_group_steps_dispatches_correctly():
    s = make_session(make_step("echo hi", note="greet"))
    assert "echo" in group_steps(s, "command")
    assert "greet" in group_steps(s, "note")
