import pytest
from breadcrumb.session import Session, Step
from breadcrumb.pinboard import (
    collect_pinned,
    format_pinboard,
    pinboard_summary,
    PinboardEntry,
)


def make_session(name="s", steps=None):
    s = Session(name=name)
    for cmd, note, pinned in (steps or []):
        step = Step(command=cmd, note=note)
        if pinned:
            step.metadata["pinned"] = True
        s.steps.append(step)
    return s


def test_collect_pinned_basic():
    s = make_session("sess", [("ls", "", True), ("pwd", "", False), ("echo hi", "greet", True)])
    entries = collect_pinned([s])
    assert len(entries) == 2
    assert entries[0].step.command == "ls"
    assert entries[1].step.command == "echo hi"


def test_collect_pinned_none():
    s = make_session("sess", [("ls", "", False), ("pwd", "", False)])
    entries = collect_pinned([s])
    assert entries == []


def test_collect_pinned_multiple_sessions():
    s1 = make_session("a", [("git pull", "", True)])
    s2 = make_session("b", [("make", "", True), ("rm -rf", "", False)])
    entries = collect_pinned([s1, s2])
    assert len(entries) == 2
    assert entries[0].session_name == "a"
    assert entries[1].session_name == "b"


def test_collect_pinned_step_index():
    s = make_session("s", [("a", "", False), ("b", "", True), ("c", "", False)])
    entries = collect_pinned([s])
    assert entries[0].step_index == 1


def test_format_pinboard_empty():
    assert format_pinboard([]) == "No pinned steps found."


def test_format_pinboard_shows_command():
    s = make_session("mysess", [("docker ps", "check containers", True)])
    entries = collect_pinned([s])
    out = format_pinboard(entries)
    assert "docker ps" in out
    assert "mysess" in out


def test_format_pinboard_verbose_shows_note():
    s = make_session("s", [("docker ps", "check containers", True)])
    entries = collect_pinned([s])
    out = format_pinboard(entries, verbose=True)
    assert "check containers" in out


def test_format_pinboard_no_note_non_verbose():
    s = make_session("s", [("docker ps", "check containers", True)])
    entries = collect_pinned([s])
    out = format_pinboard(entries, verbose=False)
    assert "check containers" not in out


def test_pinboard_summary():
    s1 = make_session("a", [("ls", "", True)])
    s2 = make_session("b", [("pwd", "", True), ("echo", "", True)])
    entries = collect_pinned([s1, s2])
    summary = pinboard_summary(entries)
    assert summary["total_pinned"] == 3
    assert summary["sessions_with_pins"] == 2


def test_pinboard_summary_empty():
    summary = pinboard_summary([])
    assert summary["total_pinned"] == 0
    assert summary["sessions_with_pins"] == 0
