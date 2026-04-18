import pytest
from breadcrumb.merger import merge_sessions, merge_summary
from breadcrumb.session import Session, Step
from datetime import datetime


def make_session(name, commands, tags=None):
    steps = [
        Step(command=cmd, note="", timestamp=datetime.utcnow().isoformat(), metadata={})
        for cmd in commands
    ]
    return Session(
        id=f"id-{name}",
        name=name,
        created_at=datetime.utcnow().isoformat(),
        steps=steps,
        tags=tags or [],
    )


def test_merge_combines_all_steps():
    a = make_session("a", ["echo hello", "ls"])
    b = make_session("b", ["pwd", "whoami"])
    merged = merge_sessions(a, b)
    assert len(merged.steps) == 4
    commands = [s.command for s in merged.steps]
    assert commands == ["echo hello", "ls", "pwd", "whoami"]


def test_merge_custom_name():
    a = make_session("a", ["ls"])
    b = make_session("b", ["pwd"])
    merged = merge_sessions(a, b, name="custom")
    assert merged.name == "custom"


def test_merge_default_name():
    a = make_session("alpha", ["ls"])
    b = make_session("beta", ["pwd"])
    merged = merge_sessions(a, b)
    assert merged.name == "alpha+beta"


def test_merge_tags_are_unioned():
    a = make_session("a", ["ls"], tags=["deploy", "prod"])
    b = make_session("b", ["pwd"], tags=["prod", "infra"])
    merged = merge_sessions(a, b)
    assert set(merged.tags) == {"deploy", "prod", "infra"}


def test_merge_skip_duplicates():
    a = make_session("a", ["ls", "pwd"])
    b = make_session("b", ["pwd", "whoami"])
    merged = merge_sessions(a, b, skip_duplicates=True)
    commands = [s.command for s in merged.steps]
    assert commands == ["ls", "pwd", "whoami"]


def test_merge_new_id_generated():
    a = make_session("a", ["ls"])
    b = make_session("b", ["pwd"])
    merged = merge_sessions(a, b)
    assert merged.id not in (a.id, b.id)


def test_merge_summary():
    a = make_session("a", ["ls"])
    b = make_session("b", ["pwd", "whoami"])
    merged = merge_sessions(a, b)
    summary = merge_summary(a, b, merged)
    assert "a" in summary
    assert "b" in summary
    assert "3 steps" in summary
