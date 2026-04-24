import pytest
from breadcrumb.session import Session, Step
from breadcrumb.scoper import (
    ScopeError,
    set_scope,
    clear_scope,
    get_scope,
    filter_by_scope,
    list_scoped,
    SCOPE_KEY,
)


def make_session(*commands: str) -> Session:
    s = Session(name="test")
    for cmd in commands:
        s.steps.append(Step(command=cmd))
    return s


def test_set_scope_valid():
    s = make_session("echo hello")
    step = set_scope(s, 0, "local")
    assert step.metadata[SCOPE_KEY] == "local"


def test_set_scope_normalizes_case():
    s = make_session("echo hello")
    set_scope(s, 0, "STAGING")
    assert s.steps[0].metadata[SCOPE_KEY] == "staging"


def test_set_scope_strips_whitespace():
    s = make_session("echo hello")
    set_scope(s, 0, "  production  ")
    assert s.steps[0].metadata[SCOPE_KEY] == "production"


def test_set_scope_invalid_raises():
    s = make_session("echo hello")
    with pytest.raises(ScopeError, match="Invalid scope"):
        set_scope(s, 0, "unknown")


def test_set_scope_empty_raises():
    s = make_session("echo hello")
    with pytest.raises(ScopeError, match="empty"):
        set_scope(s, 0, "   ")


def test_set_scope_out_of_range_raises():
    s = make_session("echo hello")
    with pytest.raises(ScopeError, match="out of range"):
        set_scope(s, 5, "local")


def test_clear_scope_removes_flag():
    s = make_session("echo hello")
    set_scope(s, 0, "ci")
    clear_scope(s, 0)
    assert SCOPE_KEY not in s.steps[0].metadata


def test_clear_scope_no_error_if_not_set():
    s = make_session("echo hello")
    step = clear_scope(s, 0)
    assert SCOPE_KEY not in step.metadata


def test_clear_scope_out_of_range_raises():
    s = make_session("echo hello")
    with pytest.raises(ScopeError):
        clear_scope(s, 99)


def test_get_scope_returns_value():
    s = make_session("make deploy")
    set_scope(s, 0, "production")
    assert get_scope(s, 0) == "production"


def test_get_scope_returns_none_if_unset():
    s = make_session("ls")
    assert get_scope(s, 0) is None


def test_filter_by_scope_returns_matching():
    s = make_session("cmd1", "cmd2", "cmd3")
    set_scope(s, 0, "local")
    set_scope(s, 2, "local")
    results = filter_by_scope(s, "local")
    assert len(results) == 2
    assert results[0].command == "cmd1"
    assert results[1].command == "cmd3"


def test_filter_by_scope_case_insensitive():
    s = make_session("cmd1")
    set_scope(s, 0, "staging")
    results = filter_by_scope(s, "STAGING")
    assert len(results) == 1


def test_filter_by_scope_empty_result():
    s = make_session("cmd1")
    results = filter_by_scope(s, "ci")
    assert results == []


def test_list_scoped_returns_indexed_tuples():
    s = make_session("a", "b", "c")
    set_scope(s, 1, "test")
    set_scope(s, 2, "ci")
    scoped = list_scoped(s)
    assert len(scoped) == 2
    assert scoped[0] == (1, s.steps[1], "test")
    assert scoped[1] == (2, s.steps[2], "ci")


def test_list_scoped_empty_when_none_set():
    s = make_session("a", "b")
    assert list_scoped(s) == []
