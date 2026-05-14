"""Tests for breadcrumb/condenser.py."""
from __future__ import annotations

import pytest

from breadcrumb.session import Session, add_step
from breadcrumb.condenser import condense_session, CondenserError


def make_session(commands) -> Session:
    s = Session(id="s1", name="test", tags=[], metadata={}, steps=[])
    for cmd in commands:
        add_step(s, command=cmd)
    return s


def test_condense_within_limit_returns_all_steps():
    s = make_session(["a", "b", "c"])
    result = condense_session(s, max_steps=5)
    assert result.condensed_count == 3
    assert result.original_count == 3


def test_condense_strategy_first():
    s = make_session(["a", "b", "c", "d", "e"])
    result = condense_session(s, max_steps=3, strategy="first")
    cmds = [step.command for step in result.session.steps]
    assert cmds == ["a", "b", "c"]


def test_condense_strategy_last():
    s = make_session(["a", "b", "c", "d", "e"])
    result = condense_session(s, max_steps=3, strategy="last")
    cmds = [step.command for step in result.session.steps]
    assert cmds == ["c", "d", "e"]


def test_condense_strategy_spread_includes_first_and_last():
    s = make_session(["a", "b", "c", "d", "e"])
    result = condense_session(s, max_steps=3, strategy="spread")
    cmds = [step.command for step in result.session.steps]
    assert cmds[0] == "a"
    assert cmds[-1] == "e"
    assert len(cmds) == 3


def test_condense_spread_single_step():
    s = make_session(["a", "b", "c"])
    result = condense_session(s, max_steps=1, strategy="spread")
    assert result.condensed_count == 1
    assert result.session.steps[0].command == "a"


def test_condense_custom_name():
    s = make_session(["a", "b"])
    result = condense_session(s, max_steps=1, name="slim")
    assert result.session.name == "slim"


def test_condense_preserves_original_name_by_default():
    s = make_session(["a", "b"])
    result = condense_session(s, max_steps=1)
    assert result.session.name == s.name


def test_condense_zero_max_raises():
    s = make_session(["a"])
    with pytest.raises(CondenserError, match="max_steps"):
        condense_session(s, max_steps=0)


def test_condense_invalid_strategy_raises():
    s = make_session(["a", "b"])
    with pytest.raises(CondenserError, match="Unknown strategy"):
        condense_session(s, max_steps=1, strategy="random")


def test_condense_summary_string():
    s = make_session(["a", "b", "c", "d"])
    result = condense_session(s, max_steps=2, strategy="first")
    summary = result.summary()
    assert "4" in summary
    assert "2" in summary


def test_condense_steps_are_independent_copies():
    s = make_session(["a", "b", "c"])
    result = condense_session(s, max_steps=2)
    result.session.steps[0].command = "CHANGED"
    assert s.steps[0].command == "a"
