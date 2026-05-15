import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from breadcrumb.scorer_cli import score_cmd
from breadcrumb.session import Session, Step
from breadcrumb.scorer import SessionScore, StepScore


@pytest.fixture
def runner():
    return CliRunner()


def make_session(name="demo", commands=None):
    s = Session(name=name)
    for cmd in (commands or ["git status", "ls -la", "echo hello"]):
        s.steps.append(Step(command=cmd))
    return s


@pytest.fixture
def mock_store():
    with patch("breadcrumb.scorer_cli._get_store") as p:
        store = MagicMock()
        p.return_value = store
        yield store


def invoke(runner, *args):
    return runner.invoke(score_cmd, list(args))


def test_show_score_output(runner, mock_store):
    session = make_session()
    mock_store.load.return_value = session
    result = invoke(runner, "show", "demo")
    assert result.exit_code == 0
    assert "Session: demo" in result.output
    assert "Total score" in result.output
    assert "Avg / step" in result.output


def test_show_score_lists_steps(runner, mock_store):
    session = make_session(commands=["git status", "ls"])
    mock_store.load.return_value = session
    result = invoke(runner, "show", "demo")
    assert result.exit_code == 0
    assert "[0]" in result.output
    assert "[1]" in result.output


def test_show_score_session_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = invoke(runner, "show", "missing")
    assert result.exit_code != 0
    assert "not found" in result.output


def test_top_cmd_output(runner, mock_store):
    session = make_session(commands=["git status", "ls -la", "echo hi", "pwd", "cat file"])
    mock_store.load.return_value = session
    result = invoke(runner, "top", "demo", "--limit", "3")
    assert result.exit_code == 0
    assert "Top 3 steps" in result.output
    assert "1." in result.output


def test_top_cmd_session_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = invoke(runner, "top", "ghost")
    assert result.exit_code != 0
    assert "not found" in result.output


def test_top_cmd_default_limit(runner, mock_store):
    session = make_session(commands=[f"cmd{i}" for i in range(10)])
    mock_store.load.return_value = session
    result = invoke(runner, "top", "demo")
    assert result.exit_code == 0
    assert "Top 5 steps" in result.output
