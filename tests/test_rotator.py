import pytest
from breadcrumb.session import Session, Step
from breadcrumb.rotator import rotate_steps, format_rotate_result, RotateError


def make_session(commands):
    s = Session(name="test")
    for cmd in commands:
        s.steps.append(Step(command=cmd))
    return s


def test_rotate_left_basic():
    s = make_session(["a", "b", "c", "d"])
    rotate_steps(s, positions=1, direction="left")
    assert [st.command for st in s.steps] == ["b", "c", "d", "a"]


def test_rotate_right_basic():
    s = make_session(["a", "b", "c", "d"])
    rotate_steps(s, positions=1, direction="right")
    assert [st.command for st in s.steps] == ["d", "a", "b", "c"]


def test_rotate_left_multiple_positions():
    s = make_session(["a", "b", "c", "d"])
    rotate_steps(s, positions=2, direction="left")
    assert [st.command for st in s.steps] == ["c", "d", "a", "b"]


def test_rotate_right_multiple_positions():
    s = make_session(["a", "b", "c", "d"])
    rotate_steps(s, positions=3, direction="right")
    assert [st.command for st in s.steps] == ["b", "c", "d", "a"]


def test_rotate_full_cycle_is_noop():
    s = make_session(["a", "b", "c"])
    rotate_steps(s, positions=3, direction="left")
    assert [st.command for st in s.steps] == ["a", "b", "c"]


def test_rotate_preserves_step_objects():
    s = make_session(["x", "y", "z"])
    original_ids = [id(st) for st in s.steps]
    rotate_steps(s, positions=1, direction="left")
    rotated_ids = [id(st) for st in s.steps]
    assert set(original_ids) == set(rotated_ids)


def test_rotate_empty_session_raises():
    s = Session(name="empty")
    with pytest.raises(RotateError, match="empty"):
        rotate_steps(s)


def test_rotate_invalid_direction_raises():
    s = make_session(["a", "b"])
    with pytest.raises(RotateError, match="direction"):
        rotate_steps(s, direction="up")


def test_rotate_zero_positions_raises():
    s = make_session(["a", "b"])
    with pytest.raises(RotateError, match="Positions"):
        rotate_steps(s, positions=0)


def test_format_rotate_result_contains_fields():
    s = make_session(["a", "b", "c"])
    result = rotate_steps(s, positions=1, direction="right")
    out = format_rotate_result(result)
    assert "right" in out
    assert "test" in out
    assert "3" in out
