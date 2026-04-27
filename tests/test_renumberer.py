"""Tests for breadcrumb.renumberer."""
import pytest

from breadcrumb.session import Session, Step
from breadcrumb.renumberer import (
    RenumberError,
    RenumberResult,
    renumber_steps,
    clear_numbers,
    get_number,
)


def make_session(n: int = 3) -> Session:
    s = Session(name="test-session")
    for i in range(n):
        s.steps.append(Step(command=f"cmd_{i}"))
    return s


def test_renumber_assigns_sequential_numbers():
    session = make_session(3)
    result = renumber_steps(session)
    assert isinstance(result, RenumberResult)
    nums = [get_number(s) for s in session.steps]
    assert nums == [1, 2, 3]


def test_renumber_custom_start():
    session = make_session(3)
    renumber_steps(session, start=10)
    nums = [get_number(s) for s in session.steps]
    assert nums == [10, 11, 12]


def test_renumber_custom_step():
    session = make_session(4)
    renumber_steps(session, start=0, step=5)
    # start must be >= 1 so use start=5
    renumber_steps(session, start=5, step=5)
    nums = [get_number(s) for s in session.steps]
    assert nums == [5, 10, 15, 20]


def test_renumber_custom_key():
    session = make_session(2)
    renumber_steps(session, key="seq")
    for s in session.steps:
        assert "seq" in s.metadata
        assert "step_number" not in s.metadata


def test_renumber_result_counts():
    session = make_session(5)
    result = renumber_steps(session)
    assert result.original_count == 5
    assert result.renumbered_count == 5


def test_renumber_summary_string():
    session = make_session(2)
    result = renumber_steps(session)
    assert "test-session" in result.summary
    assert "2" in result.summary


def test_renumber_invalid_start_raises():
    session = make_session(2)
    with pytest.raises(RenumberError, match="start"):
        renumber_steps(session, start=0)


def test_renumber_invalid_step_raises():
    session = make_session(2)
    with pytest.raises(RenumberError, match="step"):
        renumber_steps(session, step=0)


def test_renumber_blank_key_raises():
    session = make_session(2)
    with pytest.raises(RenumberError, match="key"):
        renumber_steps(session, key="   ")


def test_clear_numbers_removes_key():
    session = make_session(3)
    renumber_steps(session)
    removed = clear_numbers(session)
    assert removed == 3
    for s in session.steps:
        assert get_number(s) is None


def test_clear_numbers_returns_zero_when_no_key():
    session = make_session(3)
    removed = clear_numbers(session)
    assert removed == 0


def test_clear_numbers_blank_key_raises():
    session = make_session(1)
    with pytest.raises(RenumberError):
        clear_numbers(session, key="")


def test_get_number_returns_none_when_unset():
    session = make_session(1)
    assert get_number(session.steps[0]) is None


def test_renumber_empty_session():
    session = make_session(0)
    result = renumber_steps(session)
    assert result.original_count == 0
    assert result.renumbered_count == 0
