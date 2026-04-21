"""Tests for breadcrumb.shuffler."""

import pytest

from breadcrumb.session import Session, Step
from breadcrumb.shuffler import (
    ShuffleError,
    ShuffleResult,
    format_shuffle_result,
    shuffle_steps,
)


def make_session(commands: list[str], name: str = "test") -> Session:
    s = Session(name=name)
    for cmd in commands:
        s.steps.append(Step(command=cmd))
    return s


def test_shuffle_returns_shuffle_result():
    s = make_session(["echo a", "echo b", "echo c"])
    result = shuffle_steps(s, seed=42)
    assert isinstance(result, ShuffleResult)


def test_shuffle_uses_all_commands():
    cmds = ["echo a", "echo b", "echo c", "echo d"]
    s = make_session(cmds)
    shuffle_steps(s, seed=7)
    assert sorted(step.command for step in s.steps) == sorted(cmds)


def test_shuffle_modifies_session_in_place():
    cmds = ["echo a", "echo b", "echo c", "echo d", "echo e"]
    s = make_session(cmds)
    original_ids = [step.id for step in s.steps]
    shuffle_steps(s, seed=99)
    shuffled_ids = [step.id for step in s.steps]
    # same step objects, different order (seed 99 should change order)
    assert sorted(original_ids) == sorted(shuffled_ids)


def test_shuffle_seed_is_reproducible():
    cmds = ["a", "b", "c", "d", "e"]
    s1 = make_session(cmds)
    s2 = make_session(cmds)
    shuffle_steps(s1, seed=123)
    shuffle_steps(s2, seed=123)
    assert [st.command for st in s1.steps] == [st.command for st in s2.steps]


def test_shuffle_different_seeds_differ():
    cmds = ["a", "b", "c", "d", "e", "f"]
    s1 = make_session(cmds)
    s2 = make_session(cmds)
    shuffle_steps(s1, seed=1)
    shuffle_steps(s2, seed=2)
    # extremely unlikely to be identical with 6 elements
    assert [st.command for st in s1.steps] != [st.command for st in s2.steps]


def test_shuffle_result_original_order():
    cmds = ["x", "y", "z"]
    s = make_session(cmds)
    result = shuffle_steps(s, seed=0)
    assert result.original_order == cmds


def test_shuffle_result_new_order_matches_session():
    cmds = ["x", "y", "z"]
    s = make_session(cmds)
    result = shuffle_steps(s, seed=5)
    assert result.new_order == [st.command for st in s.steps]


def test_shuffle_raises_with_one_step():
    s = make_session(["only one"])
    with pytest.raises(ShuffleError, match="at least 2 steps"):
        shuffle_steps(s)


def test_shuffle_raises_with_empty_session():
    s = make_session([])
    with pytest.raises(ShuffleError, match="at least 2 steps"):
        shuffle_steps(s)


def test_format_shuffle_result_contains_session_name():
    s = make_session(["echo hi", "ls", "pwd"], name="my-session")
    result = shuffle_steps(s, seed=1)
    output = format_shuffle_result(result)
    assert "my-session" in output


def test_format_shuffle_result_contains_commands():
    cmds = ["echo hi", "ls", "pwd"]
    s = make_session(cmds, name="demo")
    result = shuffle_steps(s, seed=3)
    output = format_shuffle_result(result)
    for cmd in cmds:
        assert cmd in output
