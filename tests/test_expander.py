"""Tests for breadcrumb.expander."""

import pytest
from breadcrumb.session import Session, Step
from breadcrumb.expander import (
    ExpandError,
    ExpandResult,
    expand_steps,
    build_alias_map,
)


def make_session(*commands: str) -> Session:
    s = Session(id="s1", name="test")
    for cmd in commands:
        s.steps.append(Step(command=cmd))
    return s


# --- expand_steps ---

def test_expand_replaces_matching_command():
    session = make_session("gs", "gc", "echo hi")
    result = expand_steps(session, {"gs": "git status", "gc": "git commit"})
    assert session.steps[0].command == "git status"
    assert session.steps[1].command == "git commit"
    assert session.steps[2].command == "echo hi"


def test_expand_returns_correct_indices():
    session = make_session("gs", "echo hi", "gc")
    result = expand_steps(session, {"gs": "git status", "gc": "git commit"})
    assert result.expanded == [0, 2]


def test_expand_no_match_returns_empty_indices():
    session = make_session("echo hello", "ls -la")
    result = expand_steps(session, {"gs": "git status"})
    assert result.expand_count == 0
    assert result.expanded == []


def test_expand_case_insensitive_by_default():
    session = make_session("GS", "Gs")
    result = expand_steps(session, {"gs": "git status"})
    assert result.expand_count == 2
    assert session.steps[0].command == "git status"
    assert session.steps[1].command == "git status"


def test_expand_case_sensitive_no_match():
    session = make_session("GS")
    result = expand_steps(session, {"gs": "git status"}, case_sensitive=True)
    assert result.expand_count == 0
    assert session.steps[0].command == "GS"


def test_expand_empty_alias_map_raises():
    session = make_session("gs")
    with pytest.raises(ExpandError):
        expand_steps(session, {})


def test_expand_summary_with_changes():
    session = make_session("gs")
    result = expand_steps(session, {"gs": "git status"})
    assert "1" in result.summary()


def test_expand_summary_no_changes():
    session = make_session("echo hi")
    result = expand_steps(session, {"gs": "git status"})
    assert result.summary() == "No commands were expanded."


# --- build_alias_map ---

def test_build_alias_map_basic():
    pairs = ["gs=git status", "gc=git commit"]
    result = build_alias_map(pairs)
    assert result == {"gs": "git status", "gc": "git commit"}


def test_build_alias_map_strips_whitespace():
    pairs = [" gs = git status "]
    result = build_alias_map(pairs)
    assert result["gs"] == "git status"


def test_build_alias_map_missing_equals_raises():
    with pytest.raises(ExpandError, match="Invalid alias entry"):
        build_alias_map(["gs git status"])


def test_build_alias_map_blank_key_raises():
    with pytest.raises(ExpandError, match="blank"):
        build_alias_map(["=git status"])


def test_build_alias_map_blank_expansion_raises():
    with pytest.raises(ExpandError, match="blank"):
        build_alias_map(["gs="])
