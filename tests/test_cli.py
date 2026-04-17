"""Tests for the breadcrumb CLI commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from breadcrumb.cli import cli
from breadcrumb.session import Session


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_store():
    with patch("breadcrumb.cli.store") as m:
        yield m


def test_new_session(runner, mock_store):
    result = runner.invoke(cli, ["new", "my-session"])
    assert result.exit_code == 0
    assert "my-session" in result.output
    mock_store.save.assert_called_once()


def test_add_step(runner, mock_store):
    session = Session(name="test")
    mock_store.load.return_value = session
    result = runner.invoke(cli, ["add", session.id, "echo hello"])
    assert result.exit_code == 0
    assert "echo hello" in result.output
    mock_store.save.assert_called_once()


def test_add_step_session_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = runner.invoke(cli, ["add", "bad-id", "echo hi"])
    assert result.exit_code == 1
    assert "not found" in result.output


def test_list_sessions_empty(runner, mock_store):
    mock_store.list_sessions.return_value = []
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "No sessions" in result.output


def test_list_sessions(runner, mock_store):
    mock_store.list_sessions.return_value = [
        {"id": "abc123", "name": "demo", "step_count": 3}
    ]
    result = runner.invoke(cli, ["list"])
    assert "abc123" in result.output
    assert "demo" in result.output


def test_export_to_stdout(runner, mock_store):
    session = Session(name="export-test")
    session.add_step(command="ls -la")
    mock_store.load.return_value = session
    result = runner.invoke(cli, ["export", session.id])
    assert result.exit_code == 0
    assert "ls -la" in result.output


def test_delete_session(runner, mock_store):
    mock_store.delete.return_value = True
    result = runner.invoke(cli, ["delete", "some-id"])
    assert result.exit_code == 0
    assert "Deleted" in result.output


def test_delete_session_not_found(runner, mock_store):
    mock_store.delete.return_value = False
    result = runner.invoke(cli, ["delete", "ghost-id"])
    assert result.exit_code == 1
