"""Tests for breadcrumb.cli_indexer."""

import pytest
from unittest.mock import MagicMock, patch
from click.testing import CliRunner
from breadcrumb.session import Session, Step
from breadcrumb.cli_indexer import index_cmd


def make_step(command: str, note: str = "") -> Step:
    return Step(command=command, note=note)


def make_session(name: str, commands) -> Session:
    s = Session(name=name)
    for cmd in commands:
        s.steps.append(make_step(cmd))
    return s


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_store():
    store = MagicMock()
    s1 = make_session("deploy", ["git pull", "docker build ."])
    s2 = make_session("cleanup", ["rm -rf /tmp", "git status"])
    store.list_sessions.return_value = [s1.id, s2.id]
    store.load.side_effect = lambda sid: (
        s1 if sid == s1.id else s2
    )
    return store, s1, s2


def invoke(runner, mock_store, *args):
    store, s1, s2 = mock_store
    with patch("breadcrumb.cli_indexer._get_store", return_value=store):
        return runner.invoke(index_cmd, list(args))


def test_search_finds_git_commands(runner, mock_store):
    result = invoke(runner, mock_store, "search", "--command", "git")
    assert result.exit_code == 0
    assert "git pull" in result.output
    assert "git status" in result.output


def test_search_no_results(runner, mock_store):
    result = invoke(runner, mock_store, "search", "--command", "kubectl")
    assert result.exit_code == 0
    assert "No matching" in result.output


def test_search_by_session_name(runner, mock_store):
    result = invoke(runner, mock_store, "search", "--session", "deploy")
    assert result.exit_code == 0
    assert "git pull" in result.output
    assert "git status" not in result.output


def test_stats_output(runner, mock_store):
    result = invoke(runner, mock_store, "stats")
    assert result.exit_code == 0
    assert "Sessions indexed" in result.output
    assert "Total steps" in result.output
    assert "4" in result.output


def test_search_no_sessions(runner):
    store = MagicMock()
    store.list_sessions.return_value = []
    with patch("breadcrumb.cli_indexer._get_store", return_value=store):
        result = runner.invoke(index_cmd, ["search", "--command", "git"])
    assert result.exit_code == 0
    assert "No sessions" in result.output
