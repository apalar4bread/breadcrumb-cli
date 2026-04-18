import pytest
from breadcrumb.session import Session, Step
from breadcrumb.trimmer import trim_steps, trim_first, trim_last, TrimError


def make_session(num_steps=5):
    s = Session(name="test")
    for i in range(num_steps):
        s.steps.append(Step(command=f"echo {i}", note=f"step {i}"))
    return s


def test_trim_steps_basic():
    s = make_session(5)
    result = trim_steps(s, start=1, end=4)
    assert len(result.steps) == 3
    assert result.steps[0].command == "echo 1"
    assert result.steps[-1].command == "echo 3"


def test_trim_steps_preserves_metadata():
    s = make_session(3)
    result = trim_steps(s, start=0, end=2)
    assert result.id == s.id
    assert result.name == s.name
    assert result.created_at == s.created_at


def test_trim_steps_defaults_to_all():
    s = make_session(4)
    result = trim_steps(s)
    assert len(result.steps) == 4


def test_trim_steps_end_clamped():
    s = make_session(3)
    result = trim_steps(s, start=0, end=100)
    assert len(result.steps) == 3


def test_trim_steps_empty_session_raises():
    s = Session(name="empty")
    with pytest.raises(TrimError, match="no steps"):
        trim_steps(s)


def test_trim_steps_start_gte_end_raises():
    s = make_session(5)
    with pytest.raises(TrimError, match="must be less than"):
        trim_steps(s, start=3, end=3)


def test_trim_steps_start_out_of_range_raises():
    s = make_session(3)
    with pytest.raises(TrimError, match="out of range"):
        trim_steps(s, start=10, end=20)


def test_trim_steps_negative_raises():
    s = make_session(3)
    with pytest.raises(TrimError, match="non-negative"):
        trim_steps(s, start=-1, end=2)


def test_trim_first():
    s = make_session(5)
    result = trim_first(s, keep=2)
    assert len(result.steps) == 2
    assert result.steps[0].command == "echo 0"
    assert result.steps[1].command == "echo 1"


def test_trim_last():
    s = make_session(5)
    result = trim_last(s, keep=2)
    assert len(result.steps) == 2
    assert result.steps[0].command == "echo 3"
    assert result.steps[1].command == "echo 4"


def test_trim_first_zero_raises():
    s = make_session(3)
    with pytest.raises(TrimError):
        trim_first(s, keep=0)


def test_trim_last_zero_raises():
    s = make_session(3)
    with pytest.raises(TrimError):
        trim_last(s, keep=0)
