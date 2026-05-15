"""Tests for breadcrumb.cli_grapher."""

import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock
from breadcrumb.session import Session, Step
from breadcrumb.cli_grapher import graph_cmd


@pytest.fixture
def runner():
    return CliRunner()


def make_session(name="demo", commands=None):
    s = Session(name=name)
    for cmd in (commands or ["echo hello", "ls -la"]):
        s.steps.append(Step(command=cmd))
    return s


@pytest.fixture
def mock_store(monkeypatch):
    store = MagicMock()
    monkeypatch.setattr("breadcrumb.cli_grapher._get_store", lambda: store)
    return store


def invoke(runner, *args):
    return runner.invoke(graph_cmd, list(args))


def test_show_graph_output(runner, mock_store):
    mock_store.load.return_value = make_session()
    result = invoke(runner, "show", "demo")
    assert result.exit_code == 0
    assert "echo hello" in result.output
    assert "ls -la" in result.output


def test_show_graph_session_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = invoke(runner, "show", "missing")
    assert result.exit_code != 0
    assert "not found" in result.output


def test_show_graph_empty_session(runner, mock_store):
    s = Session(name="empty")
    mock_store.load.return_value = s
    result = invoke(runner, "show", "empty")
    assert result.exit_code != 0


def test_show_graph_no_edges(runner, mock_store):
    mock_store.load.return_value = make_session()
    result = invoke(runner, "show", "demo", "--no-edges")
    assert result.exit_code == 0
    assert "->" not in result.output


def test_graph_summary_output(runner, mock_store):
    mock_store.load.return_value = make_session()
    result = invoke(runner, "summary", "demo")
    assert result.exit_code == 0
    assert "nodes" in result.output
    assert "edges" in result.output


def test_graph_summary_session_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = invoke(runner, "summary", "ghost")
    assert result.exit_code != 0
    assert "not found" in result.output
