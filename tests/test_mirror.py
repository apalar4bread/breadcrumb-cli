"""Tests for breadcrumb.mirror."""

import pytest
from breadcrumb.session import Session, Step
from breadcrumb.mirror import (
    MirrorError,
    MirrorResult,
    mirror_session,
    format_mirror_result,
)


def make_session(name="demo", commands=None):
    s = Session(id="s1", name=name)
    for cmd in (commands or ["echo a", "echo b", "echo c"]):
        s.steps.append(Step(command=cmd))
    return s


def test_mirror_returns_new_session():
    s = make_session()
    result = mirror_session(s)
    assert result is not s


def test_mirror_default_name_contains_original():
    s = make_session(name="my-session")
    result = mirror_session(s)
    assert "my-session" in result.name
    assert "mirrored" in result.name


def test_mirror_custom_name():
    s = make_session()
    result = mirror_session(s, name="reversed-demo")
    assert result.name == "reversed-demo"


def test_mirror_reverses_steps_by_default():
    s = make_session(commands=["echo a", "echo b", "echo c"])
    result = mirror_session(s)
    commands = [step.command for step in result.steps]
    assert commands == ["echo c", "echo b", "echo a"]


def test_mirror_no_reverse_preserves_order():
    s = make_session(commands=["echo a", "echo b", "echo c"])
    result = mirror_session(s, reverse=False)
    commands = [step.command for step in result.steps]
    assert commands == ["echo a", "echo b", "echo c"]


def test_mirror_steps_are_independent_copies():
    s = make_session(commands=["echo a", "echo b"])
    result = mirror_session(s)
    result.steps[0].command = "changed"
    assert s.steps[-1].command == "echo b"


def test_mirror_empty_session_raises():
    s = Session(id="s1", name="empty")
    with pytest.raises(MirrorError, match="no steps"):
        mirror_session(s)


def test_mirror_blank_name_raises():
    s = make_session()
    with pytest.raises(MirrorError, match="blank"):
        mirror_session(s, name="   ")


def test_mirror_tags_are_copied():
    s = make_session()
    s.tags = ["ci", "deploy"]
    result = mirror_session(s)
    assert result.tags == ["ci", "deploy"]
    result.tags.append("extra")
    assert "extra" not in s.tags


def test_mirror_id_differs_from_original():
    s = make_session()
    result = mirror_session(s)
    assert result.id != s.id


def test_format_mirror_result_reversed():
    r = MirrorResult(
        original_name="src",
        mirrored_name="src (mirrored)",
        step_count=3,
        reversed=True,
    )
    out = format_mirror_result(r)
    assert "src" in out
    assert "reversed" in out
    assert "3" in out


def test_format_mirror_result_not_reversed():
    r = MirrorResult(
        original_name="src",
        mirrored_name="src (mirrored)",
        step_count=2,
        reversed=False,
    )
    out = format_mirror_result(r)
    assert "copied" in out
