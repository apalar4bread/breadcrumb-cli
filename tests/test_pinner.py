import pytest
from breadcrumb.session import Session, Step
from breadcrumb.pinner import pin_step, unpin_step, list_pinned, is_pinned, PinError


def make_session():
    s = Session(name="test")
    s.steps = [
        Step(command="echo hello", note="first"),
        Step(command="ls -la", note="second"),
        Step(command="pwd", note="third"),
    ]
    return s


def test_pin_step_sets_metadata():
    s = make_session()
    pin_step(s, 1)
    assert s.steps[1].metadata.get("pinned") is True


def test_pin_step_does_not_affect_others():
    s = make_session()
    pin_step(s, 0)
    assert s.steps[1].metadata.get("pinned") is not True
    assert s.steps[2].metadata.get("pinned") is not True


def test_unpin_step_removes_flag():
    s = make_session()
    pin_step(s, 2)
    assert is_pinned(s, 2)
    unpin_step(s, 2)
    assert not is_pinned(s, 2)


def test_unpin_step_no_error_if_not_pinned():
    s = make_session()
    # should not raise
    unpin_step(s, 0)
    assert not is_pinned(s, 0)


def test_list_pinned_returns_correct_indices():
    s = make_session()
    pin_step(s, 0)
    pin_step(s, 2)
    pinned = list_pinned(s)
    assert len(pinned) == 2
    assert pinned[0][0] == 0
    assert pinned[1][0] == 2


def test_list_pinned_empty_when_none():
    s = make_session()
    assert list_pinned(s) == []


def test_pin_out_of_range_raises():
    s = make_session()
    with pytest.raises(PinError):
        pin_step(s, 10)


def test_unpin_out_of_range_raises():
    s = make_session()
    with pytest.raises(PinError):
        unpin_step(s, -5)


def test_is_pinned_out_of_range_raises():
    s = make_session()
    with pytest.raises(PinError):
        is_pinned(s, 99)
