"""Tests for breadcrumb/mapper.py"""
import pytest

from breadcrumb.session import Session, Step
from breadcrumb.mapper import (
    build_map,
    top_commands,
    format_map,
    MapperError,
    CommandMap,
)


def make_session(name: str, commands) -> Session:
    s = Session(name=name)
    for cmd in commands:
        s.steps.append(Step(command=cmd))
    return s


def test_build_map_basic():
    s = make_session("s1", ["git status", "git diff", "git status"])
    cmap = build_map([s])
    assert "git status" in cmap.entries
    assert cmap.entries["git status"].count == 2


def test_build_map_case_insensitive_by_default():
    s = make_session("s1", ["Git Status", "git status"])
    cmap = build_map([s])
    assert cmap.total_commands == 1
    assert cmap.entries["git status"].count == 2


def test_build_map_case_sensitive():
    s = make_session("s1", ["Git Status", "git status"])
    cmap = build_map([s], case_sensitive=True)
    assert cmap.total_commands == 2


def test_build_map_multiple_sessions():
    s1 = make_session("s1", ["ls", "pwd"])
    s2 = make_session("s2", ["ls", "echo hi"])
    cmap = build_map([s1, s2])
    assert cmap.entries["ls"].count == 2
    assert cmap.entries["pwd"].count == 1


def test_build_map_empty_sessions_raises():
    with pytest.raises(MapperError):
        build_map([])


def test_build_map_skips_blank_commands():
    s = make_session("s1", ["ls", "", "   "])
    cmap = build_map([s])
    assert cmap.total_commands == 1


def test_build_map_occurrence_records_session_name():
    s = make_session("my-session", ["make build"])
    cmap = build_map([s])
    occ = cmap.entries["make build"].occurrences
    assert occ[0][0] == "my-session"


def test_build_map_occurrence_records_step_index():
    s = make_session("s1", ["a", "b", "a"])
    cmap = build_map([s])
    indices = [idx for _, idx in cmap.entries["a"].occurrences]
    assert indices == [0, 2]


def test_top_commands_returns_sorted():
    s = make_session("s1", ["x", "y", "y", "z", "z", "z"])
    cmap = build_map([s])
    top = top_commands(cmap, n=2)
    assert top[0].command == "z"
    assert top[1].command == "y"


def test_top_commands_respects_n():
    s = make_session("s1", ["a", "b", "c", "d", "e"])
    cmap = build_map([s])
    assert len(top_commands(cmap, n=3)) == 3


def test_format_map_empty_returns_message():
    cmap = CommandMap()
    result = format_map(cmap)
    assert "No commands" in result


def test_format_map_contains_command():
    s = make_session("s1", ["docker ps"])
    cmap = build_map([s])
    out = format_map(cmap)
    assert "docker ps" in out


def test_total_occurrences():
    s = make_session("s1", ["a", "a", "b"])
    cmap = build_map([s])
    assert cmap.total_occurrences == 3
