"""Tests for breadcrumb.cli_planner."""

import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from breadcrumb.session import Session
from breadcrumb.cli_planner import plan_cmd


@pytest.fixture
def runner():
    return CliRunner()


def make_session(name="test") -> Session:
    return Session(id="s1", name=name, steps=[], metadata={})


@pytest.fixture
def mock_store():
    with patch("breadcrumb.cli_planner._get_store") as p:
        store = MagicMock()
        p.return_value = store
        yield store


def invoke(runner, *args):
    return runner.invoke(plan_cmd, list(args))


def test_add_plan_success(runner, mock_store):
    s = make_session()
    mock_store.load.return_value = s
    result = invoke(runner, "add", "s1", "echo hello")
    assert result.exit_code == 0
    assert "echo hello" in result.output
    mock_store.save.assert_called_once_with(s)


def test_add_plan_session_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = invoke(runner, "add", "missing", "echo hi")
    assert result.exit_code == 1
    assert "not found" in result.output


def test_add_plan_empty_command(runner, mock_store):
    s = make_session()
    mock_store.load.return_value = s
    result = invoke(runner, "add", "s1", "   ")
    assert result.exit_code == 1


def test_list_plan_no_steps(runner, mock_store):
    s = make_session()
    mock_store.load.return_value = s
    result = invoke(runner, "list", "s1")
    assert result.exit_code == 0
    assert "No planned" in result.output


def test_list_plan_shows_steps(runner, mock_store):
    s = make_session()
    s.metadata["planned_steps"] = [
        {"command": "git pull", "note": "update", "order": 0, "metadata": {}}
    ]
    mock_store.load.return_value = s
    result = invoke(runner, "list", "s1")
    assert "git pull" in result.output
    assert "update" in result.output


def test_clear_plan_success(runner, mock_store):
    s = make_session()
    s.metadata["planned_steps"] = [
        {"command": "make test", "note": "", "order": 0, "metadata": {}}
    ]
    mock_store.load.return_value = s
    result = invoke(runner, "clear", "s1")
    assert result.exit_code == 0
    assert "1" in result.output
    mock_store.save.assert_called_once()


def test_promote_plan_success(runner, mock_store):
    s = make_session()
    s.metadata["planned_steps"] = [
        {"command": "docker build .", "note": "", "order": 0, "metadata": {}}
    ]
    mock_store.load.return_value = s
    result = invoke(runner, "promote", "s1", "0")
    assert result.exit_code == 0
    assert "docker build ." in result.output


def test_promote_plan_invalid_order(runner, mock_store):
    s = make_session()
    mock_store.load.return_value = s
    result = invoke(runner, "promote", "s1", "99")
    assert result.exit_code == 1
    assert "Error" in result.output
