"""tests/test_cursor.py — tests for breadcrumb.cursor"""

import pytest
from breadcrumb.session import Session, Step
from breadcrumb.cursor import (
    CursorError,
    set_cursor,
    get_cursor,
    advance_cursor,
    reset_cursor,
    is_at_end,
    _CURSOR_KEY,
)


def make_session(commands=None) -> Session:
    commands = commands or ["echo a", "echo b", "echo c"]
    s = Session(name="test")
    for cmd in commands:
        s.steps.append(Step(command=cmd))
    return s


def test_set_cursor_basic():
    s = make_session()
    result = set_cursor(s, 1)
    assert result.position == 1
    assert result.command == "echo b"
    assert result.total_steps == 3
    assert s.metadata[_CURSOR_KEY] == 1


def test_set_cursor_first_step():
    s = make_session()
    result = set_cursor(s, 0)
    assert result.position == 0
    assert result.command == "echo a"


def test_set_cursor_last_step():
    s = make_session()
    result = set_cursor(s, 2)
    assert result.position == 2
    assert result.command == "echo c"


def test_set_cursor_out_of_range_raises():
    s = make_session()
    with pytest.raises(CursorError, match="out of range"):
        set_cursor(s, 5)


def test_set_cursor_negative_raises():
    s = make_session()
    with pytest.raises(CursorError, match="out of range"):
        set_cursor(s, -1)


def test_set_cursor_empty_session_raises():
    s = Session(name="empty")
    with pytest.raises(CursorError, match="no steps"):
        set_cursor(s, 0)


def test_get_cursor_defaults_to_zero():
    s = make_session()
    result = get_cursor(s)
    assert result.position == 0
    assert result.command == "echo a"


def test_get_cursor_returns_set_position():
    s = make_session()
    set_cursor(s, 2)
    result = get_cursor(s)
    assert result.position == 2


def test_get_cursor_empty_session_raises():
    s = Session(name="empty")
    with pytest.raises(CursorError):
        get_cursor(s)


def test_advance_cursor_moves_forward():
    s = make_session()
    set_cursor(s, 0)
    result = advance_cursor(s, by=2)
    assert result.position == 2


def test_advance_cursor_clamps_at_end():
    s = make_session()
    set_cursor(s, 2)
    result = advance_cursor(s, by=10)
    assert result.position == 2


def test_advance_cursor_default_step_is_one():
    s = make_session()
    set_cursor(s, 0)
    result = advance_cursor(s)
    assert result.position == 1


def test_reset_cursor_removes_key():
    s = make_session()
    set_cursor(s, 2)
    reset_cursor(s)
    assert _CURSOR_KEY not in s.metadata


def test_reset_cursor_no_error_if_not_set():
    s = make_session()
    reset_cursor(s)  # should not raise


def test_is_at_end_true():
    s = make_session()
    set_cursor(s, 2)
    assert is_at_end(s) is True


def test_is_at_end_false():
    s = make_session()
    set_cursor(s, 1)
    assert is_at_end(s) is False


def test_is_at_end_empty_session():
    s = Session(name="empty")
    assert is_at_end(s) is False


def test_cursor_result_str():
    s = make_session()
    result = set_cursor(s, 0)
    text = str(result)
    assert "test" in text
    assert "echo a" in text
    assert "1/3" in text
