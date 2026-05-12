"""Tests for the flagger CLI commands."""
from unittest.mock import MagicMock, patch
import pytest
from click.testing import CliRunner
from breadcrumb.session import Session, Step
from breadcrumb.cli_flagger import flag_cmd


@pytest.fixture
def runner():
    return CliRunner()


def make_session(cmds=None):
    s = Session(id="abc", name="demo")
    for cmd in (cmds or ["ls", "pwd", "whoami"]):
        s.steps.append(Step(command=cmd))
    return s


@pytest.fixture
def mock_store(monkeypatch):
    store = MagicMock()
    monkeypatch.setattr("breadcrumb.cli_flagger._get_store", lambda: store)
    return store


def invoke(runner, *args):
    return runner.invoke(flag_cmd, list(args))


def test_set_flag_success(runner, mock_store):
    s = make_session()
    mock_store.load.return_value = s
    result = invoke(runner, "set", "abc", "0", "todo")
    assert result.exit_code == 0
    assert "todo" in result.output
    mock_store.save.assert_called_once_with(s)


def test_set_flag_session_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = invoke(runner, "set", "missing", "0", "todo")
    assert result.exit_code != 0
    assert "not found" in result.output


def test_set_flag_invalid_flag(runner, mock_store):
    s = make_session()
    mock_store.load.return_value = s
    result = invoke(runner, "set", "abc", "0", "nonsense")
    assert result.exit_code != 0
    assert "Unknown flag" in result.output


def test_clear_flag_success(runner, mock_store):
    s = make_session()
    s.steps[0].metadata["flags"] = ["done"]
    mock_store.load.return_value = s
    result = invoke(runner, "clear", "abc", "0", "done")
    assert result.exit_code == 0
    assert "cleared" in result.output


def test_list_flags_with_flags(runner, mock_store):
    s = make_session()
    s.steps[1].metadata["flags"] = ["review", "warn"]
    mock_store.load.return_value = s
    result = invoke(runner, "list", "abc", "1")
    assert result.exit_code == 0
    assert "review" in result.output
    assert "warn" in result.output


def test_list_flags_empty(runner, mock_store):
    s = make_session()
    mock_store.load.return_value = s
    result = invoke(runner, "list", "abc", "0")
    assert result.exit_code == 0
    assert "No flags" in result.output


def test_find_by_flag_found(runner, mock_store):
    s = make_session()
    s.steps[2].metadata["flags"] = ["skip"]
    mock_store.load.return_value = s
    result = invoke(runner, "find", "abc", "skip")
    assert result.exit_code == 0
    assert "whoami" in result.output


def test_find_by_flag_none(runner, mock_store):
    s = make_session()
    mock_store.load.return_value = s
    result = invoke(runner, "find", "abc", "done")
    assert result.exit_code == 0
    assert "No steps" in result.output
