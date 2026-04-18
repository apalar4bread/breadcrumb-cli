import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock
from breadcrumb.session import Session, Step
from breadcrumb.cli_duplicates import dupes_cmd


@pytest.fixture
def runner():
    return CliRunner()


def make_session(commands, name="mysession"):
    s = Session(name=name)
    for cmd in commands:
        s.steps.append(Step(command=cmd))
    return s


@pytest.fixture
def mock_store():
    return MagicMock()


def invoke(runner, mock_store, *args):
    return runner.invoke(dupes_cmd, args, obj={"store": mock_store})


def test_find_no_duplicates(runner, mock_store):
    mock_store.load.return_value = make_session(["ls", "pwd"])
    result = invoke(runner, mock_store, "find", "mysession")
    assert "No duplicate steps found" in result.output


def test_find_duplicates_listed(runner, mock_store):
    mock_store.load.return_value = make_session(["ls", "ls"])
    result = invoke(runner, mock_store, "find", "mysession")
    assert "1 duplicate pair" in result.output
    assert "'ls'" in result.output


def test_find_session_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = invoke(runner, mock_store, "find", "ghost")
    assert "not found" in result.output


def test_remove_duplicates(runner, mock_store):
    mock_store.load.return_value = make_session(["ls", "pwd", "ls"])
    result = invoke(runner, mock_store, "remove", "mysession")
    assert "Removed 1" in result.output
    mock_store.save.assert_called_once()


def test_remove_dry_run(runner, mock_store):
    mock_store.load.return_value = make_session(["ls", "ls"])
    result = invoke(runner, mock_store, "remove", "mysession", "--dry-run")
    assert "dry-run" in result.output
    mock_store.save.assert_not_called()


def test_remove_session_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = invoke(runner, mock_store, "remove", "ghost")
    assert "not found" in result.output
