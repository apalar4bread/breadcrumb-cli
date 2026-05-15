"""Tests for breadcrumb.classifier."""

import pytest

from breadcrumb.session import Session, Step
from breadcrumb.classifier import (
    classify_step,
    classify_session,
    ClassifyError,
    ClassifyResult,
)


def make_session(*commands: str) -> Session:
    s = Session(id="s1", name="test")
    for cmd in commands:
        s.steps.append(Step(command=cmd))
    return s


def test_classify_step_git():
    step = Step(command="git commit -m 'msg'")
    assert classify_step(step) == "git"


def test_classify_step_docker():
    step = Step(command="docker build .")
    assert classify_step(step) == "docker"


def test_classify_step_file():
    step = Step(command="cp foo bar")
    assert classify_step(step) == "file"


def test_classify_step_network():
    step = Step(command="curl https://example.com")
    assert classify_step(step) == "network"


def test_classify_step_package():
    step = Step(command="pip install requests")
    assert classify_step(step) == "package"


def test_classify_step_python():
    step = Step(command="pytest tests/")
    assert classify_step(step) == "python"


def test_classify_step_shell():
    step = Step(command="echo hello")
    assert classify_step(step) == "shell"


def test_classify_step_unknown_returns_other():
    step = Step(command="make build")
    assert classify_step(step) == "other"


def test_classify_step_case_insensitive():
    step = Step(command="Git status")
    assert classify_step(step) == "git"


def test_classify_session_basic():
    s = make_session("git status", "docker ps", "echo hi")
    result = classify_session(s)
    assert isinstance(result, ClassifyResult)
    assert 0 in result.categories["git"]
    assert 1 in result.categories["docker"]
    assert 2 in result.categories["shell"]
    assert result.uncategorized == []


def test_classify_session_uncategorized():
    s = make_session("make all", "./run.sh")
    result = classify_session(s)
    assert result.uncategorized == [0, 1]
    assert result.total_classified == 0


def test_classify_session_mixed():
    s = make_session("git pull", "make test", "pip install -r requirements.txt")
    result = classify_session(s)
    assert 0 in result.categories["git"]
    assert 0 in result.uncategorized
    assert 1 in result.categories["package"]


def test_classify_session_empty_raises():
    s = Session(id="s1", name="empty")
    with pytest.raises(ClassifyError, match="no steps"):
        classify_session(s)


def test_classify_result_summary_contains_category():
    s = make_session("git log", "git diff")
    result = classify_session(s)
    summary = result.summary()
    assert "git" in summary
    assert "2 step" in summary
