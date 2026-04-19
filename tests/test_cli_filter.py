import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from breadcrumb.cli_filter import filter_cmd
from breadcrumb.session import Session, Step


@pytest.fixture
def runner():
    return CliRunner()


def make_session():
    s = Session(name="mysession")
    s.steps = [
        Step(command="git status", note="check status", metadata={}),
        Step(command="git commit -m 'x'", note=None, metadata={"pinned": True}),
        Step(command="make build", note="build project", metadata={}),
    ]
    return s


@pytest.fixture
def mock_store():
    with patch("breadcrumb.cli_filter._get_store") as p:
        store = MagicMock()
        store.load.return_value = make_session()
        p.return_value = store
        yield store


def invoke(runner, *args):
    return runner.invoke(filter_cmd, list(args))


def test_filter_by_command_found(runner, mock_store):
    result = invoke(runner, "command", "mysession", "git")
    assert result.exit_code == 0
    assert "git status" in result.output
    assert "git commit" in result.output


def test_filter_by_command_not_found(runner, mock_store):
    result = invoke(runner, "command", "mysession", "kubectl")
    assert result.exit_code == 0
    assert "No matching" in result.output


def test_filter_by_command_session_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = invoke(runner, "command", "ghost", "git")
    assert result.exit_code != 0
    assert "not found" in result.output


def test_filter_by_note_found(runner, mock_store):
    result = invoke(runner, "note", "mysession", "status")
    assert result.exit_code == 0
    assert "git status" in result.output


def test_filter_by_note_not_found(runner, mock_store):
    result = invoke(runner, "note", "mysession", "nonexistent")
    assert "No matching" in result.output


def test_filter_by_meta_found(runner, mock_store):
    result = invoke(runner, "meta", "mysession", "pinned")
    assert result.exit_code == 0
    assert "git commit" in result.output


def test_filter_by_meta_not_found(runner, mock_store):
    result = invoke(runner, "meta", "mysession", "label")
    assert "No matching" in result.output
