"""Tests for breadcrumb.planner."""

import pytest
from breadcrumb.session import Session
from breadcrumb.planner import (
    PlanError,
    PlannedStep,
    add_planned_step,
    list_planned,
    clear_planned,
    promote_planned,
)


def make_session(name="test") -> Session:
    return Session(id="s1", name=name, steps=[], metadata={})


def test_add_planned_step_basic():
    s = make_session()
    step = add_planned_step(s, "echo hello")
    assert step.command == "echo hello"
    assert step.order == 0


def test_add_planned_step_with_note():
    s = make_session()
    step = add_planned_step(s, "ls -la", note="list files")
    assert step.note == "list files"


def test_add_planned_step_strips_whitespace():
    s = make_session()
    step = add_planned_step(s, "  pwd  ", note="  cwd  ")
    assert step.command == "pwd"
    assert step.note == "cwd"


def test_add_planned_step_empty_raises():
    s = make_session()
    with pytest.raises(PlanError):
        add_planned_step(s, "")


def test_add_planned_step_blank_raises():
    s = make_session()
    with pytest.raises(PlanError):
        add_planned_step(s, "   ")


def test_add_planned_step_auto_order():
    s = make_session()
    add_planned_step(s, "step one")
    step2 = add_planned_step(s, "step two")
    assert step2.order == 1


def test_add_planned_step_custom_order():
    s = make_session()
    step = add_planned_step(s, "step", order=5)
    assert step.order == 5


def test_list_planned_sorted_by_order():
    s = make_session()
    add_planned_step(s, "third", order=2)
    add_planned_step(s, "first", order=0)
    add_planned_step(s, "second", order=1)
    steps = list_planned(s)
    assert [p.command for p in steps] == ["first", "second", "third"]


def test_list_planned_empty():
    s = make_session()
    assert list_planned(s) == []


def test_clear_planned_returns_count():
    s = make_session()
    add_planned_step(s, "a")
    add_planned_step(s, "b")
    removed = clear_planned(s)
    assert removed == 2
    assert list_planned(s) == []


def test_clear_planned_empty_session():
    s = make_session()
    assert clear_planned(s) == 0


def test_promote_planned_creates_real_step():
    s = make_session()
    add_planned_step(s, "git status", order=0)
    promote_planned(s, order=0)
    assert len(s.steps) == 1
    assert s.steps[0].command == "git status"


def test_promote_planned_removes_from_plan():
    s = make_session()
    add_planned_step(s, "make build", order=0)
    promote_planned(s, order=0)
    assert list_planned(s) == []


def test_promote_planned_invalid_order_raises():
    s = make_session()
    add_planned_step(s, "echo hi", order=0)
    with pytest.raises(PlanError):
        promote_planned(s, order=99)


def test_planned_step_roundtrip():
    ps = PlannedStep(command="docker ps", note="check containers", order=3)
    restored = PlannedStep.from_dict(ps.to_dict())
    assert restored.command == ps.command
    assert restored.note == ps.note
    assert restored.order == ps.order
