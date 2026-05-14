import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from breadcrumb.session import Session, Step
from breadcrumb.splitter_cli import split_cmd


@pytest.fixture
def runner():
    return CliRunner()


def make_session(name="mysession", commands=None):
    session = Session(id="abc123", name=name)
    for cmd in (commands or ["echo a", "echo b", "echo c", "echo d"]):
        session.steps.append(Step(command=cmd))
    return session


@pytest.fixture
def mock_store():
    with patch("breadcrumb.splitter_cli._get_store") as factory:
        store = MagicMock()
        factory.return_value = store
        yield store


def invoke(runner, *args):
    return runner.invoke(split_cmd, list(args), catch_exceptions=False)


def test_run_split_success(runner, mock_store):
    session = make_session()
    mock_store.load.return_value = session
    result = invoke(runner, "run", "abc123", "2")
    assert result.exit_code == 0
    assert "Part A" in result.output or "steps" in result.output


def test_run_split_session_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = runner.invoke(split_cmd, ["run", "missing", "2"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_run_split_invalid_index(runner, mock_store):
    session = make_session(commands=["echo a"])
    mock_store.load.return_value = session
    result = runner.invoke(split_cmd, ["run", "abc123", "99"])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_run_split_saves_when_flag_set(runner, mock_store):
    session = make_session()
    mock_store.load.return_value = session
    result = invoke(runner, "run", "abc123", "2", "--save")
    assert result.exit_code == 0
    assert mock_store.save.call_count == 2


def test_preview_split_shows_commands(runner, mock_store):
    session = make_session(commands=["ls", "pwd", "whoami", "date"])
    mock_store.load.return_value = session
    result = invoke(runner, "preview", "abc123", "2")
    assert result.exit_code == 0
    assert "ls" in result.output
    assert "whoami" in result.output


def test_preview_split_session_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = runner.invoke(split_cmd, ["preview", "ghost", "1"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_run_split_custom_names(runner, mock_store):
    session = make_session()
    mock_store.load.return_value = session
    result = invoke(runner, "run", "abc123", "2", "--name-a", "first", "--name-b", "second")
    assert result.exit_code == 0
    assert "first" in result.output or "second" in result.output
