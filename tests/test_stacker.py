"""Tests for breadcrumb/stacker.py."""

import pytest
from breadcrumb.session import Session, Step
from breadcrumb.stacker import (
    StackError,
    push_step,
    pop_step,
    peek_step,
    format_stack_result,
)


def make_session(name: str, commands: list) -> Session:
    s = Session(name=name)
    for cmd in commands:
        s.steps.append(Step(command=cmd))
    return s


# --- push_step ---

def test_push_step_moves_last_by_default():
    src = make_session("src", ["echo a", "echo b"])
    dst = make_session("dst", [])
    result = push_step(src, dst)
    assert result.moved_step.command == "echo b"
    assert len(src.steps) == 1
    assert len(dst.steps) == 1
    assert dst.steps[0].command == "echo b"


def test_push_step_moves_by_index():
    src = make_session("src", ["echo a", "echo b", "echo c"])
    dst = make_session("dst", [])
    result = push_step(src, dst, index=0)
    assert result.moved_step.command == "echo a"
    assert src.steps[0].command == "echo b"
    assert result.remaining_count == 2


def test_push_step_empty_source_raises():
    src = make_session("src", [])
    dst = make_session("dst", [])
    with pytest.raises(StackError, match="no steps"):
        push_step(src, dst)


def test_push_step_invalid_index_raises():
    src = make_session("src", ["echo a"])
    dst = make_session("dst", [])
    with pytest.raises(StackError, match="out of range"):
        push_step(src, dst, index=5)


def test_push_step_result_fields():
    src = make_session("alpha", ["ls"])
    dst = make_session("beta", [])
    result = push_step(src, dst)
    assert result.source_session == "alpha"
    assert result.target_session == "beta"
    assert result.remaining_count == 0


# --- pop_step ---

def test_pop_step_removes_last():
    s = make_session("s", ["a", "b", "c"])
    step = pop_step(s)
    assert step.command == "c"
    assert len(s.steps) == 2


def test_pop_step_by_index():
    s = make_session("s", ["a", "b", "c"])
    step = pop_step(s, index=1)
    assert step.command == "b"
    assert len(s.steps) == 2


def test_pop_step_empty_raises():
    s = make_session("s", [])
    with pytest.raises(StackError, match="no steps"):
        pop_step(s)


def test_pop_step_bad_index_raises():
    s = make_session("s", ["a"])
    with pytest.raises(StackError, match="out of range"):
        pop_step(s, index=99)


# --- peek_step ---

def test_peek_step_does_not_remove():
    s = make_session("s", ["x", "y"])
    step = peek_step(s)
    assert step.command == "y"
    assert len(s.steps) == 2


def test_peek_step_by_index():
    s = make_session("s", ["x", "y", "z"])
    step = peek_step(s, index=0)
    assert step.command == "x"


def test_peek_step_empty_raises():
    s = make_session("s", [])
    with pytest.raises(StackError, match="no steps"):
        peek_step(s)


# --- format_stack_result ---

def test_format_stack_result_contains_key_info():
    src = make_session("src", ["git status"])
    dst = make_session("dst", [])
    result = push_step(src, dst)
    text = format_stack_result(result)
    assert "git status" in text
    assert "src" in text
    assert "dst" in text
    assert "0 step(s) remaining" in text
