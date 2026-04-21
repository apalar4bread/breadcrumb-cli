import pytest
from breadcrumb.session import Session, add_step
from breadcrumb.composer import compose_session, compose_summary, ComposeError


def make_session(name: str, commands) -> Session:
    s = Session(name=name)
    for cmd in commands:
        add_step(s, command=cmd, note=f"note for {cmd}")
    return s


def test_compose_basic():
    s1 = make_session("alpha", ["echo hello", "ls -la", "pwd"])
    s2 = make_session("beta", ["git status", "git diff"])
    result = compose_session([(s1, [0, 2]), (s2, [1])], name="my-compose")
    assert result.name == "my-compose"
    assert len(result.steps) == 3
    assert result.steps[0].command == "echo hello"
    assert result.steps[1].command == "pwd"
    assert result.steps[2].command == "git diff"


def test_compose_preserves_notes():
    s1 = make_session("alpha", ["echo hello"])
    result = compose_session([(s1, [0])], name="notes-check")
    assert result.steps[0].note == "note for echo hello"


def test_compose_preserves_metadata():
    s = Session(name="meta-src")
    add_step(s, command="make build", metadata={"pinned": True, "label": "build"})
    result = compose_session([(s, [0])], name="meta-compose")
    assert result.steps[0].metadata["pinned"] is True
    assert result.steps[0].metadata["label"] == "build"


def test_compose_metadata_is_independent_copy():
    s = Session(name="src")
    add_step(s, command="cmd", metadata={"x": 1})
    result = compose_session([(s, [0])], name="copy-check")
    result.steps[0].metadata["x"] = 99
    assert s.steps[0].metadata["x"] == 1


def test_compose_blank_name_raises():
    s = make_session("src", ["echo"])
    with pytest.raises(ComposeError, match="blank"):
        compose_session([(s, [0])], name="   ")


def test_compose_out_of_range_raises():
    s = make_session("src", ["echo"])
    with pytest.raises(ComposeError, match="out of range"):
        compose_session([(s, [5])], name="bad")


def test_compose_negative_index_raises():
    s = make_session("src", ["echo"])
    with pytest.raises(ComposeError, match="out of range"):
        compose_session([(s, [-1])], name="bad")


def test_compose_no_steps_raises():
    s = make_session("src", ["echo"])
    with pytest.raises(ComposeError, match="no steps"):
        compose_session([(s, [])], name="empty")


def test_compose_multiple_sources_order():
    s1 = make_session("a", ["step-a0", "step-a1"])
    s2 = make_session("b", ["step-b0"])
    result = compose_session([(s2, [0]), (s1, [1])], name="ordered")
    assert result.steps[0].command == "step-b0"
    assert result.steps[1].command == "step-a1"


def test_compose_summary_text():
    s1 = make_session("alpha", ["a", "b"])
    s2 = make_session("beta", ["c"])
    result = compose_session([(s1, [0, 1]), (s2, [0])], name="summary-test")
    summary = compose_summary(result, [(s1, [0, 1]), (s2, [0])])
    assert "summary-test" in summary
    assert "3" in summary
    assert "alpha" in summary
    assert "beta" in summary
