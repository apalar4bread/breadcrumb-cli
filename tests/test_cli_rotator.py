import pytest
from unittest.mock import MagicMock, patch
from click.testing import CliRunner
from breadcrumb.session import Session, Step
from breadcrumb.cli_rotator import rotate_cmd


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
    with patch("breadcrumb.cli_rotator._get_store") as factory:
        store = MagicMock()
        factory.return_value = store
        yield store


def invoke(runner, *args):
    return runner.invoke(rotate_cmd, list(args), catch_exceptions=False)


def test_rotate_left_output(runner, mock_store):
    mock_store.load.return_value = make_session("demo", ["a", "b", "c"])
    result = invoke(runner, "left", "demo")
    assert result.exit_code == 0
    assert "left" in result.output
    assert "demo" in result.output


def test_rotate_right_output(runner, mock_store):
    mock_store.load.return_value = make_session("demo", ["x", "y", "z"])
    result = invoke(runner, "right", "demo", "--positions", "2")
    assert result.exit_code == 0
    assert "right" in result.output


def test_rotate_left_session_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = runner.invoke(rotate_cmd, ["left", "missing"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_rotate_right_session_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = runner.invoke(rotate_cmd, ["right", "missing"])
    assert result.exit_code != 0


def test_rotate_left_saves_when_flag_set(runner, mock_store):
    session = make_session("demo", ["a", "b", "c"])
    mock_store.load.return_value = session
    result = invoke(runner, "left", "demo", "--save")
    assert result.exit_code == 0
    mock_store.save.assert_called_once_with(session)
    assert "saved" in result.output.lower()


def test_rotate_left_no_save_by_default(runner, mock_store):
    mock_store.load.return_value = make_session("demo", ["a", "b"])
    invoke(runner, "left", "demo")
    mock_store.save.assert_not_called()
