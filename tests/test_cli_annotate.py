import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from breadcrumb.cli_annotate import annotate_cmd
from breadcrumb.session import Session, Step


@pytest.fixture
def runner():
    return CliRunner()


def make_session():
    s = Session(name="demo")
    s.steps = [Step(command="echo hi"), Step(command="ls")]
    return s


@pytest.fixture
def mock_store():
    with patch("breadcrumb.cli_annotate._get_store") as m:
        store = MagicMock()
        m.return_value = store
        yield store


def invoke(runner, *args):
    return runner.invoke(annotate_cmd, list(args))


def test_set_comment(runner, mock_store):
    mock_store.load.return_value = make_session()
    result = invoke(runner, "set", "demo", "0", "greets user")
    assert result.exit_code == 0
    assert "greets user" in result.output
    mock_store.save.assert_called_once()


def test_set_comment_session_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = invoke(runner, "set", "nope", "0", "hi")
    assert result.exit_code == 1
    assert "not found" in result.output


def test_set_comment_invalid_index(runner, mock_store):
    mock_store.load.return_value = make_session()
    result = invoke(runner, "set", "demo", "99", "hi")
    assert result.exit_code == 1
    assert "Error" in result.output


def test_clear_comment(runner, mock_store):
    s = make_session()
    s.steps[0].metadata["comment"] = "old note"
    mock_store.load.return_value = s
    result = invoke(runner, "clear", "demo", "0")
    assert result.exit_code == 0
    assert "Cleared" in result.output


def test_clear_comment_session_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = invoke(runner, "clear", "ghost", "0")
    assert result.exit_code == 1


def test_list_no_annotations(runner, mock_store):
    mock_store.load.return_value = make_session()
    result = invoke(runner, "list", "demo")
    assert result.exit_code == 0
    assert "No annotated" in result.output


def test_list_with_annotations(runner, mock_store):
    s = make_session()
    s.steps[1].metadata["comment"] = "lists files"
    mock_store.load.return_value = s
    result = invoke(runner, "list", "demo")
    assert result.exit_code == 0
    assert "lists files" in result.output
    assert "ls" in result.output
