"""Tests for breadcrumb.namer."""

import pytest

from breadcrumb.session import Session, Step
from breadcrumb.namer import (
    NamerError,
    suggest_name,
    auto_name,
    apply_suggested_name,
)


def make_session(name: str = "test", commands=()) -> Session:
    s = Session(name=name)
    for cmd in commands:
        s.steps.append(Step(command=cmd))
    return s


def test_suggest_name_basic():
    s = make_session(commands=["git commit", "git push", "git status"])
    name = suggest_name(s)
    assert "git" in name


def test_suggest_name_empty_session_raises():
    s = make_session(commands=[])
    with pytest.raises(NamerError, match="no steps"):
        suggest_name(s)


def test_suggest_name_blank_commands_raises():
    s = make_session(commands=["  ", ""])
    with pytest.raises(NamerError):
        suggest_name(s)


def test_suggest_name_returns_hyphen_joined():
    s = make_session(commands=["docker build .", "docker run app", "docker stop app"])
    name = suggest_name(s)
    assert "-" in name or len(name) > 0


def test_suggest_name_max_words_respected():
    s = make_session(commands=["alpha beta gamma delta epsilon"])
    name = suggest_name(s, max_words=2)
    parts = name.split("-")
    assert len(parts) <= 2


def test_auto_name_falls_back_on_empty():
    s = make_session(commands=[])
    name = auto_name(s, prefix="run")
    assert name == "run-0-steps"


def test_auto_name_uses_suggest_when_possible():
    s = make_session(commands=["pytest tests", "pytest --cov"])
    name = auto_name(s)
    assert "pytest" in name


def test_apply_suggested_name_replaces_untitled():
    s = make_session(name="untitled", commands=["make build", "make test"])
    applied = apply_suggested_name(s)
    assert applied != "untitled"
    assert s.name == applied


def test_apply_suggested_name_keeps_existing():
    s = make_session(name="my-deploy", commands=["kubectl apply -f deploy.yaml"])
    result = apply_suggested_name(s)
    assert result == "my-deploy"
    assert s.name == "my-deploy"


def test_apply_suggested_name_override_replaces_any():
    s = make_session(name="my-deploy", commands=["npm install", "npm run build"])
    result = apply_suggested_name(s, override=True)
    assert "npm" in result or "install" in result or "run" in result
    assert s.name == result


def test_apply_suggested_name_new_session_placeholder():
    s = make_session(name="new session", commands=["cargo build", "cargo test"])
    result = apply_suggested_name(s)
    assert result != "new session"
