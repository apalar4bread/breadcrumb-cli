"""Tests for breadcrumb.cli_repeater."""

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from breadcrumb.session import Session, Step
from breadcrumb.cli_repeater import repeat_cmd


@pytest.fixture
def runner():
    return CliRunner()


def make_session(name="demo", commands=None):
    steps = [
        Step(command=cmd, note="", metadata={}, timestamp="2024-01-01T00:00:00")
        for cmd in (commands or ["ls", "pwd"])
    ]
    return Session(
        id="abc",
        name=name,
        created_at="2024-01-01T00:00:00",
        steps=steps,
        tags=[],
        metadata={},
    )


@pytest.fixture
def mock_store():
    store = MagicMock()
    store.load.return_value = make_session()
    return store


def invoke(runner, mock_store, *args):
    with patch("breadcrumb.cli_repeater._get_store", return_value=mock_store):
        return runner.invoke(repeat_cmd, list(args))


def test_mark_success(runner, mock_store):
    result = invoke(runner, mock_store, "mark", "demo", "0", "--times", "3")
    assert result.exit_code == 0
    assert "Marked step 0" in result.output
    mock_store.save.assert_called_once()


def test_mark_session_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = invoke(runner, mock_store, "mark", "ghost", "0")
    assert result.exit_code != 0
    assert "not found" in result.output


def test_mark_invalid_times_shows_error(runner, mock_store):
    result = invoke(runner, mock_store, "mark", "demo", "0", "--times", "1")
    assert result.exit_code != 0


def test_clear_success(runner, mock_store):
    # pre-mark the step
    mock_store.load.return_value.steps[0].metadata["repeat"] = "2"
    result = invoke(runner, mock_store, "clear", "demo", "0")
    assert result.exit_code == 0
    assert "Cleared" in result.output


def test_clear_session_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = invoke(runner, mock_store, "clear", "ghost", "0")
    assert result.exit_code != 0


def test_expand_prints_steps(runner, mock_store):
    result = invoke(runner, mock_store, "expand", "demo")
    assert result.exit_code == 0
    assert "[0]" in result.output


def test_expand_with_save(runner, mock_store):
    result = invoke(runner, mock_store, "expand", "demo", "--save")
    assert result.exit_code == 0
    assert "Saved as" in result.output
    mock_store.save.assert_called()


def test_expand_custom_name(runner, mock_store):
    result = invoke(runner, mock_store, "expand", "demo", "--name", "my-expanded", "--save")
    assert result.exit_code == 0
    assert "my-expanded" in result.output
