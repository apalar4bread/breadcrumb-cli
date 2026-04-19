import pytest
from breadcrumb.session import Session, Step
from breadcrumb.splitter import split_session, split_summary, SplitError
from datetime import datetime, timezone


def make_session(n_steps: int = 4) -> Session:
    steps = [
        Step(command=f"cmd{i}", note=f"note{i}", timestamp=datetime.now(timezone.utc).isoformat(), metadata={})
        for i in range(n_steps)
    ]
    return Session(id="abc", name="test", created_at=datetime.now(timezone.utc).isoformat(), steps=steps, tags=["x"])


def test_split_basic():
    s = make_session(4)
    a, b = split_session(s, at=2)
    assert len(a.steps) == 2
    assert len(b.steps) == 2


def test_split_first_part_commands():
    s = make_session(4)
    a, b = split_session(s, at=1)
    assert a.steps[0].command == "cmd0"
    assert b.steps[0].command == "cmd1"


def test_split_custom_names():
    s = make_session(4)
    a, b = split_session(s, at=2, name_a="alpha", name_b="beta")
    assert a.name == "alpha"
    assert b.name == "beta"


def test_split_default_names():
    s = make_session(4)
    a, b = split_session(s, at=2)
    assert "part 1" in a.name
    assert "part 2" in b.name


def test_split_ids_are_new():
    s = make_session(4)
    a, b = split_session(s, at=2)
    assert a.id != s.id
    assert b.id != s.id
    assert a.id != b.id


def test_split_tags_are_copied():
    s = make_session(4)
    a, b = split_session(s, at=2)
    assert a.tags == ["x"]
    assert b.tags == ["x"]


def test_split_at_zero_raises():
    s = make_session(4)
    with pytest.raises(SplitError):
        split_session(s, at=0)


def test_split_at_end_raises():
    s = make_session(4)
    with pytest.raises(SplitError):
        split_session(s, at=4)


def test_split_empty_session_raises():
    s = make_session(0)
    with pytest.raises(SplitError):
        split_session(s, at=0)


def test_split_summary_contains_names():
    s = make_session(4)
    a, b = split_session(s, at=2)
    summary = split_summary(a, b)
    assert a.name in summary
    assert b.name in summary
    assert "2 step" in summary
