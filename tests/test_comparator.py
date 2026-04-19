import pytest
from breadcrumb.session import Session, Step
from breadcrumb.comparator import compare_sessions, format_compare


def make_session(name, commands):
    s = Session(name=name)
    for cmd in commands:
        s.steps.append(Step(command=cmd))
    return s


def test_identical_commands():
    a = make_session("a", ["ls", "pwd"])
    b = make_session("b", ["ls", "pwd"])
    r = compare_sessions(a, b)
    assert r.similarity_pct == 100.0
    assert sorted(r.common_commands) == ["ls", "pwd"]
    assert r.only_in_a == []
    assert r.only_in_b == []


def test_no_overlap():
    a = make_session("a", ["ls"])
    b = make_session("b", ["pwd"])
    r = compare_sessions(a, b)
    assert r.similarity_pct == 0.0
    assert r.common_commands == []
    assert r.only_in_a == ["ls"]
    assert r.only_in_b == ["pwd"]


def test_partial_overlap():
    a = make_session("a", ["ls", "pwd", "echo hi"])
    b = make_session("b", ["ls", "git status"])
    r = compare_sessions(a, b)
    assert r.common_commands == ["ls"]
    assert "pwd" in r.only_in_a
    assert "git status" in r.only_in_b
    assert 0 < r.similarity_pct < 100


def test_case_insensitive():
    a = make_session("a", ["LS"])
    b = make_session("b", ["ls"])
    r = compare_sessions(a, b)
    assert r.similarity_pct == 100.0


def test_empty_sessions():
    a = make_session("a", [])
    b = make_session("b", [])
    r = compare_sessions(a, b)
    assert r.similarity_pct == 100.0
    assert r.common_commands == []


def test_one_empty():
    a = make_session("a", ["ls"])
    b = make_session("b", [])
    r = compare_sessions(a, b)
    assert r.similarity_pct == 0.0
    assert r.only_in_a == ["ls"]


def test_format_compare_contains_names():
    a = make_session("alpha", ["ls"])
    b = make_session("beta", ["pwd"])
    r = compare_sessions(a, b)
    out = format_compare(r)
    assert "alpha" in out
    assert "beta" in out
    assert "Similarity" in out
