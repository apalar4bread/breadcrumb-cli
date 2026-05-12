import pytest
from breadcrumb.session import Session, Step
from breadcrumb.pinboard import (
    collect_pinned,
    format_pinboard,
    PinboardEntry,
    PinboardError,
)


def make_session(name, commands, pinned_indices=None):
    s = Session(name=name)
    for i, cmd in enumerate(commands):
        step = Step(command=cmd)
        if pinned_indices and i in pinned_indices:
            step.metadata["pinned"] = True
        s.steps.append(step)
    return s


def test_collect_returns_pinboard_entries():
    s = make_session("demo", ["ls", "pwd"], pinned_indices=[1])
    entries = collect_pinned([s])
    assert len(entries) == 1
    assert isinstance(entries[0], PinboardEntry)


def test_entry_has_correct_session_name():
    s = make_session("myses", ["echo hi"], pinned_indices=[0])
    entries = collect_pinned([s])
    assert entries[0].session_name == "myses"


def test_entry_has_correct_step_index():
    s = make_session("s", ["a", "b", "c"], pinned_indices=[2])
    entries = collect_pinned([s])
    assert entries[0].step_index == 2


def test_format_pinboard_includes_command():
    s = make_session("s", ["npm install"], pinned_indices=[0])
    entries = collect_pinned([s])
    text = format_pinboard(entries)
    assert "npm install" in text


def test_format_pinboard_includes_session_name():
    s = make_session("deploy-session", ["kubectl apply -f ."  ], pinned_indices=[0])
    entries = collect_pinned([s])
    text = format_pinboard(entries)
    assert "deploy-session" in text


def test_collect_pinned_across_multiple_sessions():
    s1 = make_session("s1", ["a", "b"], pinned_indices=[0])
    s2 = make_session("s2", ["c", "d"], pinned_indices=[1])
    entries = collect_pinned([s1, s2])
    commands = [e.step.command for e in entries]
    assert "a" in commands
    assert "d" in commands


def test_collect_pinned_empty_list_returns_empty():
    entries = collect_pinned([])
    assert entries == []
