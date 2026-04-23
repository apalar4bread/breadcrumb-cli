"""Tests for breadcrumb.injector."""

import pytest

from breadcrumb.session import Session, add_step
from breadcrumb.injector import (
    InjectError,
    inject_step,
    inject_after,
    format_inject_result,
)


def make_session(*commands):
    s = Session(id="s1", name="test")
    for cmd in commands:
        add_step(s, cmd)
    return s


# --- inject_step ---

def test_inject_at_start():
    s = make_session("echo b", "echo c")
    result = inject_step(s, 0, "echo a")
    assert s.steps[0].command == "echo a"
    assert result.inserted_at == 0


def test_inject_at_end():
    s = make_session("echo a", "echo b")
    result = inject_step(s, 2, "echo c")
    assert s.steps[2].command == "echo c"
    assert result.inserted_at == 2


def test_inject_in_middle():
    s = make_session("echo a", "echo c")
    inject_step(s, 1, "echo b")
    assert [step.command for step in s.steps] == ["echo a", "echo b", "echo c"]


def test_inject_preserves_existing_steps():
    s = make_session("ls", "pwd")
    inject_step(s, 1, "whoami")
    assert s.steps[0].command == "ls"
    assert s.steps[2].command == "pwd"


def test_inject_with_note():
    s = make_session("ls")
    inject_step(s, 0, "echo hi", note="greeting")
    assert s.steps[0].note == "greeting"


def test_inject_with_metadata():
    s = make_session("ls")
    inject_step(s, 0, "echo hi", metadata={"env": "prod"})
    assert s.steps[0].metadata["env"] == "prod"


def test_inject_empty_command_raises():
    s = make_session("ls")
    with pytest.raises(InjectError, match="empty"):
        inject_step(s, 0, "")


def test_inject_blank_command_raises():
    s = make_session("ls")
    with pytest.raises(InjectError, match="empty"):
        inject_step(s, 0, "   ")


def test_inject_negative_position_raises():
    s = make_session("ls")
    with pytest.raises(InjectError, match="out of range"):
        inject_step(s, -1, "echo hi")


def test_inject_position_too_large_raises():
    s = make_session("ls")  # 1 step, valid positions: 0, 1
    with pytest.raises(InjectError, match="out of range"):
        inject_step(s, 5, "echo hi")


def test_inject_into_empty_session_at_zero():
    s = make_session()
    inject_step(s, 0, "echo hello")
    assert len(s.steps) == 1
    assert s.steps[0].command == "echo hello"


# --- inject_after ---

def test_inject_after_basic():
    s = make_session("echo a", "echo c")
    inject_after(s, 0, "echo b")
    assert [st.command for st in s.steps] == ["echo a", "echo b", "echo c"]


# --- format_inject_result ---

def test_format_inject_result_contains_command():
    s = make_session("ls")
    result = inject_step(s, 0, "pwd")
    out = format_inject_result(result)
    assert "pwd" in out
    assert "0" in out
