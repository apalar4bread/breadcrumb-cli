from unittest.mock import MagicMock, patch
import pytest
from click.testing import CliRunner
from breadcrumb.session import Session, Step
from breadcrumb.cli_transposer import transpose_cmd


@pytest.fixture
def runner():
    return CliRunner()


def make_session(name, commands):
    s = Session(name=name)
    for cmd in commands:
        s.steps.append(Step(command=cmd))
    return s


@pytest.fixture
def mock_store():
    with patch("breadcrumb.cli_transposer._get_store") as p:
        store = MagicMock()
        p.return_value = store
        yield store


def invoke(runner, *args):
    return runner.invoke(transpose_cmd, list(args), catch_exceptions=False)


def test_swap_success(runner, mock_store):
    s = make_session("demo", ["echo a", "echo b", "echo c"])
    mock_store.load.return_value = s
    result = invoke(runner, "swap", "demo", "0", "2")
    assert result.exit_code == 0
    assert "Swapped" in result.output
    mock_store.save.assert_called_once()


def test_swap_dry_run_does_not_save(runner, mock_store):
    s = make_session("demo", ["echo a", "echo b"])
    mock_store.load.return_value = s
    result = invoke(runner, "swap", "demo", "0", "1", "--dry-run")
    assert result.exit_code == 0
    assert "dry run" in result.output
    mock_store.save.assert_not_called()


def test_swap_session_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = runner.invoke(transpose_cmd, ["swap", "ghost", "0", "1"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_swap_same_index_error(runner, mock_store):
    s = make_session("demo", ["a", "b"])
    mock_store.load.return_value = s
    result = runner.invoke(transpose_cmd, ["swap", "demo", "1", "1"])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_swap_output_contains_commands(runner, mock_store):
    s = make_session("demo", ["ls", "pwd"])
    mock_store.load.return_value = s
    result = invoke(runner, "swap", "demo", "0", "1")
    assert "ls" in result.output
    assert "pwd" in result.output
