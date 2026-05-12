import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from breadcrumb.tagger_cli import tag_cmd
from breadcrumb.session import Session


@pytest.fixture
def runner():
    return CliRunner()


def make_session(name="demo", tags=None):
    s = Session(name=name)
    if tags:
        s.metadata["tags"] = tags
    return s


@pytest.fixture
def mock_store():
    store = MagicMock()
    store.list_sessions.return_value = ["demo", "other"]
    return store


def invoke(runner, mock_store, *args):
    with patch("breadcrumb.tagger_cli._get_store", return_value=mock_store):
        return runner.invoke(tag_cmd, list(args))


def test_add_tag_success(runner, mock_store):
    session = make_session()
    mock_store.load.return_value = session
    result = invoke(runner, mock_store, "add", "demo", "python")
    assert result.exit_code == 0
    assert "python" in result.output
    mock_store.save.assert_called_once_with(session)


def test_add_tag_session_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = invoke(runner, mock_store, "add", "missing", "python")
    assert result.exit_code == 1
    assert "not found" in result.output


def test_remove_tag_success(runner, mock_store):
    session = make_session(tags=["python", "dev"])
    mock_store.load.return_value = session
    result = invoke(runner, mock_store, "remove", "demo", "python")
    assert result.exit_code == 0
    assert "python" in result.output
    mock_store.save.assert_called_once()


def test_remove_tag_session_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = invoke(runner, mock_store, "remove", "missing", "python")
    assert result.exit_code == 1


def test_list_tags_with_tags(runner, mock_store):
    session = make_session(tags=["alpha", "beta"])
    mock_store.load.return_value = session
    result = invoke(runner, mock_store, "list", "demo")
    assert result.exit_code == 0
    assert "alpha" in result.output
    assert "beta" in result.output


def test_list_tags_empty(runner, mock_store):
    session = make_session()
    mock_store.load.return_value = session
    result = invoke(runner, mock_store, "list", "demo")
    assert result.exit_code == 0
    assert "No tags" in result.output


def test_find_sessions_by_tag(runner, mock_store):
    s1 = make_session("demo", tags=["python"])
    s2 = make_session("other", tags=["rust"])
    mock_store.load.side_effect = lambda name: {"demo": s1, "other": s2}.get(name)
    result = invoke(runner, mock_store, "find", "python")
    assert result.exit_code == 0
    assert "demo" in result.output
    assert "other" not in result.output


def test_find_no_sessions_with_tag(runner, mock_store):
    s1 = make_session("demo", tags=["rust"])
    s2 = make_session("other", tags=["go"])
    mock_store.load.side_effect = lambda name: {"demo": s1, "other": s2}.get(name)
    result = invoke(runner, mock_store, "find", "python")
    assert result.exit_code == 0
    assert "No sessions" in result.output
