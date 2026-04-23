"""Tests for breadcrumb.cli_injector."""

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from breadcrumb.session import Session, add_step
from breadcrumb.cli_injector import inject_cmd


@pytest.fixture
def runner():
    return CliRunner()


def make_session(*commands):
    s = Session(id="s1", name="mysession")
    for cmd in commands:
        add_step(s, cmd)
    return s


@pytest.fixture
def mock_store():
    with patch("breadcrumb.cli_injector._get_store") as mock_factory:
        store = MagicMock()
        mock_factory.return_value = store
        yield store


def invoke(runner, *args):
    return runner.invoke(inject_cmd, list(args))


def test_inject_at_success(runner, mock_store):
    s = make_session("echo b", "echo c")
    mock_store.load.return_value = s
    result = invoke(runner, "at", "mysession", "0", "echo a")
    assert result.exit_code == 0
    assert "echo a" in result.output
    assert "position 0" in result.output
    mock_store.save.assert_called_once()


def test_inject_at_with_note(runner, mock_store):
    s = make_session("ls")
    mock_store.load.return_value = s
    result = invoke(runner, "at", "mysession", "0", "pwd", "--note", "check dir")
    assert result.exit_code == 0
    assert s.steps[0].note == "check dir"


def test_inject_at_session_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = invoke(runner, "at", "ghost", "0", "echo hi")
    assert result.exit_code != 0
    assert "not found" in result.output


def test_inject_at_invalid_position(runner, mock_store):
    s = make_session("ls")
    mock_store.load.return_value = s
    result = invoke(runner, "at", "mysession", "99", "echo hi")
    assert result.exit_code != 0
    assert "Error" in result.output


def test_inject_after_success(runner, mock_store):
    s = make_session("echo a", "echo c")
    mock_store.load.return_value = s
    result = invoke(runner, "after", "mysession", "0", "echo b")
    assert result.exit_code == 0
    assert s.steps[1].command == "echo b"
    mock_store.save.assert_called_once()


def test_inject_after_session_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = invoke(runner, "after", "ghost", "0", "echo hi")
    assert result.exit_code != 0
    assert "not found" in result.output


def test_inject_at_with_meta(runner, mock_store):
    s = make_session("ls")
    mock_store.load.return_value = s
    result = invoke(runner, "at", "mysession", "0", "pwd", "--meta", "env=prod")
    assert result.exit_code == 0
    assert s.steps[0].metadata.get("env") == "prod"
