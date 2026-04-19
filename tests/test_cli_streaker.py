"""Tests for cli_streaker commands."""
import pytest
from unittest.mock import MagicMock, patch
from click.testing import CliRunner
from datetime import datetime, timezone, timedelta
from breadcrumb.session import Session, Step
from breadcrumb.cli_streaker import streak_cmd


@pytest.fixture
def runner():
    return CliRunner()


def make_session(days_ago_list):
    s = Session(id="s1", name="test")
    for d in days_ago_list:
        ts = (datetime.now(timezone.utc) - timedelta(days=d)).strftime("%Y-%m-%dT10:00:00")
        s.steps.append(Step(command="ls", timestamp=ts))
    return s


@pytest.fixture
def mock_store():
    store = MagicMock()
    store.list_sessions.return_value = ["s1"]
    store.load.return_value = make_session([0, 1, 2])
    return store


def invoke(runner, cmd, args, store):
    with patch("breadcrumb.cli_streaker._get_store", return_value=store):
        return runner.invoke(cmd, args)


def test_show_streak_output(runner, mock_store):
    result = invoke(runner, streak_cmd, ["show"], mock_store)
    assert result.exit_code == 0
    assert "streak" in result.output.lower() or "day" in result.output.lower()


def test_show_streak_no_sessions(runner):
    store = MagicMock()
    store.list_sessions.return_value = []
    result = invoke(runner, streak_cmd, ["show"], store)
    assert result.exit_code == 0
    assert "No sessions" in result.output


def test_summary_output(runner, mock_store):
    result = invoke(runner, streak_cmd, ["summary"], mock_store)
    assert result.exit_code == 0
    assert "Streak" in result.output
    assert "day" in result.output


def test_summary_no_sessions(runner):
    store = MagicMock()
    store.list_sessions.return_value = []
    result = invoke(runner, streak_cmd, ["summary"], store)
    assert result.exit_code == 0
    assert "0" in result.output
