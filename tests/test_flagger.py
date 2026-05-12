"""Tests for breadcrumb.flagger."""
import pytest
from breadcrumb.session import Session, Step
from breadcrumb.flagger import (
    FlagError,
    set_flag,
    clear_flag,
    get_flags,
    find_by_flag,
    clear_all_flags,
)


def make_session(commands=None):
    s = Session(id="s1", name="test")
    for cmd in (commands or ["echo a", "echo b", "echo c"]):
        s.steps.append(Step(command=cmd))
    return s


def test_set_flag_basic():
    s = make_session()
    set_flag(s, 0, "todo")
    assert "todo" in get_flags(s, 0)


def test_set_flag_normalizes_case():
    s = make_session()
    set_flag(s, 0, "DONE")
    assert "done" in get_flags(s, 0)


def test_set_flag_idempotent():
    s = make_session()
    set_flag(s, 0, "review")
    set_flag(s, 0, "review")
    assert get_flags(s, 0).count("review") == 1


def test_set_flag_invalid_raises():
    s = make_session()
    with pytest.raises(FlagError, match="Unknown flag"):
        set_flag(s, 0, "bogus")


def test_set_flag_empty_raises():
    s = make_session()
    with pytest.raises(FlagError, match="empty"):
        set_flag(s, 0, "   ")


def test_set_flag_out_of_range_raises():
    s = make_session()
    with pytest.raises(FlagError, match="out of range"):
        set_flag(s, 99, "todo")


def test_clear_flag_removes_flag():
    s = make_session()
    set_flag(s, 1, "warn")
    clear_flag(s, 1, "warn")
    assert "warn" not in get_flags(s, 1)


def test_clear_flag_no_error_if_absent():
    s = make_session()
    clear_flag(s, 0, "skip")  # should not raise


def test_clear_flag_does_not_affect_others():
    s = make_session()
    set_flag(s, 0, "todo")
    set_flag(s, 0, "review")
    clear_flag(s, 0, "todo")
    assert "review" in get_flags(s, 0)
    assert "todo" not in get_flags(s, 0)


def test_find_by_flag_returns_correct_indices():
    s = make_session()
    set_flag(s, 0, "done")
    set_flag(s, 2, "done")
    assert find_by_flag(s, "done") == [0, 2]


def test_find_by_flag_empty_when_none_set():
    s = make_session()
    assert find_by_flag(s, "todo") == []


def test_clear_all_flags_removes_everything():
    s = make_session()
    set_flag(s, 0, "todo")
    set_flag(s, 0, "review")
    clear_all_flags(s, 0)
    assert get_flags(s, 0) == []


def test_multiple_flags_on_same_step():
    s = make_session()
    set_flag(s, 1, "todo")
    set_flag(s, 1, "warn")
    flags = get_flags(s, 1)
    assert "todo" in flags
    assert "warn" in flags
