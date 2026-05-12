import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock
from breadcrumb.pinboard_cli import pinboard_cmd
from breadcrumb.session import Session, Step


@pytest.fixture
def runner():
    return CliRunner()


def make_session(name, commands, pinned_indices=None):
    s = Session(name=name)
    for i, cmd in enumerate(commands):
        step = Step(command=cmd)
        if pinned_indices and i in pinned_indices:
            step.metadata["pinned"] = True
        s.steps.append(step)
    return s


@pytest.fixture
def mock_store(monkeypatch):
    store = MagicMock()
    monkeypatch.setattr("breadcrumb.pinboard_cli._get_store", lambda _: store)
    return store


def invoke(runner, cmd, args, store, sessions):
    store.list.return_value = [s.name for s in sessions]
    store.load.side_effect = lambda name: next(s for s in sessions if s.name == name)
    return runner.invoke(cmd, args, catch_exceptions=False)


def test_show_pinboard_with_pins(runner, mock_store):
    sessions = [make_session("s1", ["git status", "ls"], pinned_indices=[0])]
    result = invoke(runner, pinboard_cmd, ["show"], mock_store, sessions)
    assert result.exit_code == 0
    assert "git status" in result.output


def test_show_pinboard_no_pins(runner, mock_store):
    sessions = [make_session("s1", ["echo hello"])]
    result = invoke(runner, pinboard_cmd, ["show"], mock_store, sessions)
    assert result.exit_code == 0
    assert "No pinned steps found" in result.output


def test_show_pinboard_empty_store(runner, mock_store):
    result = invoke(runner, pinboard_cmd, ["show"], mock_store, [])
    assert result.exit_code == 0
    assert "No pinned steps found" in result.output


def test_count_pinned(runner, mock_store):
    sessions = [
        make_session("s1", ["cmd1", "cmd2"], pinned_indices=[0, 1]),
        make_session("s2", ["cmd3"], pinned_indices=[0]),
    ]
    result = invoke(runner, pinboard_cmd, ["count"], mock_store, sessions)
    assert result.exit_code == 0
    assert "3" in result.output


def test_count_pinned_none(runner, mock_store):
    sessions = [make_session("s1", ["cmd1"])]
    result = invoke(runner, pinboard_cmd, ["count"], mock_store, sessions)
    assert result.exit_code == 0
    assert "0" in result.output


def test_show_multiple_sessions(runner, mock_store):
    sessions = [
        make_session("s1", ["make build"], pinned_indices=[0]),
        make_session("s2", ["docker run"], pinned_indices=[0]),
    ]
    result = invoke(runner, pinboard_cmd, ["show"], mock_store, sessions)
    assert result.exit_code == 0
    assert "make build" in result.output
    assert "docker run" in result.output
