import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from breadcrumb.tagger_cli import tag_cmd
from breadcrumb.session import Session, Step
from datetime import datetime


@pytest.fixture
def runner():
    return CliRunner()


def make_session(name="test", tags=None):
    s = Session(id="abc123", name=name, steps=[])
    s.tags = tags or []
    return s


@pytest.fixture
def mock_store():
    store = MagicMock()
    return store


def invoke(runner, mock_store, args):
    with patch("breadcrumb.tagger_cli._get_store", return_value=mock_store):
        return runner.invoke(tag_cmd, args)


def test_add_tag_success(runner, mock_store):
    session = make_session()
    mock_store.load.return_value = session
    result = invoke(runner, mock_store, ["add", "abc123", "deploy"])
    assert result.exit_code == 0
    assert "deploy" in result.output
    mock_store.save.assert_called_once()


def test_add_tag_session_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = invoke(runner, mock_store, ["add", "missing", "deploy"])
    assert result.exit_code == 1


def test_remove_tag_success(runner, mock_store):
    session = make_session(tags=["deploy"])
    mock_store.load.return_value = session
    result = invoke(runner, mock_store, ["remove", "abc123", "deploy"])
    assert result.exit_code == 0
    mock_store.save.assert_called_once()


def test_remove_tag_session_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = invoke(runner, mock_store, ["remove", "missing", "deploy"])
    assert result.exit_code == 1


def test_list_tags_with_tags(runner, mock_store):
    session = make_session(tags=["alpha", "beta"])
    mock_store.load.return_value = session
    result = invoke(runner, mock_store, ["list", "abc123"])
    assert result.exit_code == 0
    assert "alpha" in result.output
    assert "beta" in result.output


def test_list_tags_empty(runner, mock_store):
    session = make_session(tags=[])
    mock_store.load.return_value = session
    result = invoke(runner, mock_store, ["list", "abc123"])
    assert result.exit_code == 0
    assert "No tags" in result.output


def test_find_sessions_by_tag(runner, mock_store):
    s1 = make_session(name="session-one", tags=["deploy"])
    s1.id = "id1"
    s2 = make_session(name="session-two", tags=["test"])
    s2.id = "id2"
    mock_store.list_sessions.return_value = ["id1", "id2"]
    mock_store.load.side_effect = lambda sid: s1 if sid == "id1" else s2
    result = invoke(runner, mock_store, ["find", "deploy"])
    assert result.exit_code == 0
    assert "session-one" in result.output
    assert "session-two" not in result.output
