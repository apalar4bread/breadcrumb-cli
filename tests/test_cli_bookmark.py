import pytest
from unittest.mock import MagicMock, patch
from click.testing import CliRunner
from breadcrumb.cli_bookmark import bookmark_cmd
from breadcrumb.session import Session, Step


@pytest.fixture
def runner():
    return CliRunner()


def make_session(name="mysession"):
    s = Session(name=name)
    s.steps = [Step(command="echo hi"), Step(command="ls")]
    return s


@pytest.fixture
def mock_store():
    with patch("breadcrumb.cli_bookmark._get_store") as mock:
        store = MagicMock()
        mock.return_value = store
        yield store


def invoke(runner, *args):
    return runner.invoke(bookmark_cmd, list(args))


def test_add_bookmark_success(runner, mock_store):
    mock_store.load.return_value = make_session()
    result = invoke(runner, "add", "mysession", "0")
    assert result.exit_code == 0
    assert "Bookmarked step 0" in result.output
    mock_store.save.assert_called_once()


def test_add_bookmark_session_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = invoke(runner, "add", "ghost", "0")
    assert result.exit_code != 0
    assert "not found" in result.output


def test_add_bookmark_out_of_range(runner, mock_store):
    mock_store.load.return_value = make_session()
    result = invoke(runner, "add", "mysession", "99")
    assert result.exit_code != 0
    assert "Error" in result.output


def test_remove_bookmark_success(runner, mock_store):
    s = make_session()
    s.steps[1].metadata["bookmarked"] = True
    mock_store.load.return_value = s
    result = invoke(runner, "remove", "mysession", "1")
    assert result.exit_code == 0
    assert "Removed bookmark" in result.output


def test_list_bookmarks_none(runner, mock_store):
    mock_store.load.return_value = make_session()
    result = invoke(runner, "list", "mysession")
    assert result.exit_code == 0
    assert "No bookmarked" in result.output


def test_list_bookmarks_shows_steps(runner, mock_store):
    s = make_session()
    s.steps[0].metadata["bookmarked"] = True
    mock_store.load.return_value = s
    result = invoke(runner, "list", "mysession")
    assert result.exit_code == 0
    assert "echo hi" in result.output
