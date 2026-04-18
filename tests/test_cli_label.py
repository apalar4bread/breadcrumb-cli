import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from breadcrumb.session import Session, Step
from breadcrumb.cli_label import label_cmd


@pytest.fixture
def runner():
    return CliRunner()


def make_session(name="mysession"):
    s = Session(name=name)
    s.steps = [Step(command="echo hi"), Step(command="ls")]
    return s


@pytest.fixture
def mock_store():
    with patch("breadcrumb.cli_label._get_store") as p:
        store = MagicMock()
        p.return_value = store
        yield store


def invoke(runner, *args):
    return runner.invoke(label_cmd, list(args))


def test_set_label_success(runner, mock_store):
    mock_store.load.return_value = make_session()
    result = invoke(runner, "set", "mysession", "0", "high")
    assert result.exit_code == 0
    assert "high" in result.output
    mock_store.save.assert_called_once()


def test_set_label_invalid(runner, mock_store):
    mock_store.load.return_value = make_session()
    result = invoke(runner, "set", "mysession", "0", "urgent")
    assert result.exit_code != 0
    assert "Error" in result.output


def test_set_label_session_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = invoke(runner, "set", "ghost", "0", "low")
    assert result.exit_code != 0
    assert "not found" in result.output


def test_clear_label_success(runner, mock_store):
    s = make_session()
    s.steps[0].metadata["label"] = "todo"
    mock_store.load.return_value = s
    result = invoke(runner, "clear", "mysession", "0")
    assert result.exit_code == 0
    assert "cleared" in result.output


def test_find_label_found(runner, mock_store):
    s = make_session()
    s.steps[1].metadata["label"] = "done"
    mock_store.load.return_value = s
    result = invoke(runner, "find", "mysession", "done")
    assert result.exit_code == 0
    assert "ls" in result.output


def test_find_label_none(runner, mock_store):
    mock_store.load.return_value = make_session()
    result = invoke(runner, "find", "mysession", "critical")
    assert result.exit_code == 0
    assert "No steps" in result.output
