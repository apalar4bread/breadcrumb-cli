import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from breadcrumb.cli_group import group_cmd
from breadcrumb.session import Session, Step


@pytest.fixture
def runner():
    return CliRunner()


def make_session(name="demo"):
    s = Session(name=name)
    s.steps = [
        Step(command="git status", note="check"),
        Step(command="git push", note="deploy"),
        Step(command="ls -la", note="check"),
    ]
    return s


@pytest.fixture
def mock_store(monkeypatch):
    store = MagicMock()
    monkeypatch.setattr("breadcrumb.cli_group._get_store", lambda: store)
    return store


def invoke(runner, *args):
    return runner.invoke(group_cmd, list(args))


def test_group_by_command_lists_groups(runner, mock_store):
    mock_store.load.return_value = make_session()
    result = invoke(runner, "by", "demo", "command")
    assert result.exit_code == 0
    assert "git" in result.output
    assert "ls" in result.output


def test_group_by_note_with_counts(runner, mock_store):
    mock_store.load.return_value = make_session()
    result = invoke(runner, "by", "demo", "note", "--counts")
    assert result.exit_code == 0
    assert "check: 2" in result.output
    assert "deploy: 1" in result.output


def test_group_session_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = invoke(runner, "by", "missing", "command")
    assert result.exit_code != 0
    assert "not found" in result.output


def test_group_empty_session(runner, mock_store):
    s = Session(name="empty")
    s.steps = []
    mock_store.load.return_value = s
    result = invoke(runner, "by", "empty", "command")
    assert result.exit_code == 0
    assert "No steps" in result.output


def test_group_by_label_shows_unlabeled(runner, mock_store):
    mock_store.load.return_value = make_session()
    result = invoke(runner, "by", "demo", "label")
    assert result.exit_code == 0
    assert "(unlabeled)" in result.output
