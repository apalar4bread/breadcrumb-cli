import pytest
from breadcrumb.session import Session, Step
from breadcrumb.statistics import (
    steps_per_day,
    average_steps_per_session,
    most_active_day,
    command_frequency,
    session_stats,
)


def make_step(command, note="", day="2024-01-01"):
    return Step(command=command, note=note, timestamp=f"{day}T12:00:00")


def make_session(name="s", steps=None):
    s = Session(name=name)
    for st in (steps or []):
        s.steps.append(st)
    return s


def test_steps_per_day_basic():
    session = make_session(steps=[
        make_step("ls", day="2024-01-01"),
        make_step("pwd", day="2024-01-01"),
        make_step("echo", day="2024-01-02"),
    ])
    result = steps_per_day(session)
    assert result == {"2024-01-01": 2, "2024-01-02": 1}


def test_steps_per_day_empty():
    session = make_session(steps=[])
    assert steps_per_day(session) == {}


def test_average_steps_empty():
    assert average_steps_per_session([]) == 0.0


def test_average_steps():
    s1 = make_session(steps=[make_step("a"), make_step("b")])
    s2 = make_session(steps=[make_step("c")])
    assert average_steps_per_session([s1, s2]) == 1.5


def test_most_active_day():
    session = make_session(steps=[
        make_step("a", day="2024-01-01"),
        make_step("b", day="2024-01-02"),
        make_step("c", day="2024-01-02"),
    ])
    assert most_active_day(session) == "2024-01-02"


def test_most_active_day_empty():
    assert most_active_day(make_session()) is None


def test_command_frequency():
    s1 = make_session(steps=[make_step("ls"), make_step("ls"), make_step("pwd")])
    s2 = make_session(steps=[make_step("ls")])
    freq = command_frequency([s1, s2])
    assert freq["ls"] == 3
    assert freq["pwd"] == 1


def test_session_stats_basic():
    session = make_session(steps=[
        make_step("ls", note="list files"),
        make_step("ls"),
        make_step("pwd"),
    ])
    stats = session_stats(session)
    assert stats["total_steps"] == 3
    assert stats["unique_commands"] == 2
    assert stats["steps_with_notes"] == 1
    assert stats["top_command"] == "ls"


def test_session_stats_empty():
    stats = session_stats(make_session())
    assert stats["total_steps"] == 0
    assert stats["top_command"] is None
