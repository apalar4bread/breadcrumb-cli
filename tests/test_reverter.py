import pytest
from breadcrumb.session import Session, Step
from breadcrumb.reverter import (
    revert_to_step,
    revert_last_n,
    format_revert_result,
    RevertError,
)


def make_session(n_steps: int = 4) -> Session:
    s = Session(name="test-session")
    for i in range(n_steps):
        s.steps.append(Step(command=f"cmd{i}", note=f"note{i}"))
    return s


def test_revert_to_step_basic():
    s = make_session(4)
    result = revert_to_step(s, 1)
    assert len(s.steps) == 2
    assert result.original_step_count == 4
    assert result.reverted_step_count == 2


def test_revert_to_step_last():
    s = make_session(3)
    result = revert_to_step(s, 2)
    assert len(s.steps) == 3
    assert result.reverted_step_count == 3


def test_revert_to_step_first():
    s = make_session(3)
    revert_to_step(s, 0)
    assert len(s.steps) == 1
    assert s.steps[0].command == "cmd0"


def test_revert_to_step_out_of_range():
    s = make_session(3)
    with pytest.raises(RevertError, match="out of range"):
        revert_to_step(s, 5)


def test_revert_to_step_negative_index():
    s = make_session(3)
    with pytest.raises(RevertError, match=">= 0"):
        revert_to_step(s, -1)


def test_revert_to_step_empty_session():
    s = Session(name="empty")
    with pytest.raises(RevertError, match="no steps"):
        revert_to_step(s, 0)


def test_revert_last_n_basic():
    s = make_session(4)
    result = revert_last_n(s, 2)
    assert len(s.steps) == 2
    assert result.original_step_count == 4
    assert result.reverted_step_count == 2


def test_revert_last_n_all():
    s = make_session(3)
    result = revert_last_n(s, 3)
    assert len(s.steps) == 0


def test_revert_last_n_too_many():
    s = make_session(2)
    with pytest.raises(RevertError, match="Cannot remove"):
        revert_last_n(s, 5)


def test_revert_last_n_zero_raises():
    s = make_session(3)
    with pytest.raises(RevertError, match="positive integer"):
        revert_last_n(s, 0)


def test_format_revert_result():
    s = make_session(4)
    result = revert_to_step(s, 1)
    msg = format_revert_result(result)
    assert "test-session" in msg
    assert "4 -> 2" in msg
    assert "2 removed" in msg
